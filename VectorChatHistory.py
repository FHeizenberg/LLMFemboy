import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime
import json
import os


class VectorChatHistory:
    def __init__(self, embedding_model_name='sentence-transformers/all-MPNet-base-v2', index_file='chat_index.faiss',
                 meta_file='chat_meta.json', max_messages=150):
        # Инициализация модели для эмбеддингов
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Размерность эмбеддингов (зависит от модели)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Инициализация FAISS индекса
        self.index = faiss.IndexFlatL2(self.embedding_dim)

        # Хранение метаданных
        self.metadata = []
        self.index_file = index_file
        self.meta_file = meta_file

        # Загрузка сохраненных данных, если они существуют
        self._load_from_disk()
        self.max_messages = max_messages

    def _load_from_disk(self):
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, 'r') as f:
                self.metadata = json.load(f)

    def _save_to_disk(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'w') as f:
            json.dump(self.metadata, f)

    def add_message(self, role, message):

        if (len(self.metadata) >= self.max_messages) and (len(self.metadata) % 15 == 0):
            self._remove_oldest_messages(percent=20)
        # Генерация эмбеддинга
        embedding = self.embedding_model.encode(message)
        embedding = np.array([embedding]).astype('float32')

        # Добавление в индекс FAISS
        self.index.add(embedding)

        # Сохранение метаданных
        self.metadata.append({
            'role': role,
            'message': message,
            'timestamp': str(datetime.now())
        })

        # Сохранение на диск
        self._save_to_disk()

    def search_similar_messages(self, query, k=3):
        # Генерация эмбеддинга для запроса
        query_embedding = self.embedding_model.encode(query)
        query_embedding = np.array([query_embedding]).astype('float32')

        # Поиск k ближайших соседей
        distances, indices = self.index.search(query_embedding, k)

        # Возврат результатов с метаданными
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= 0 and idx < len(self.metadata):  # Проверка на валидность индекса
                result = self.metadata[idx].copy()
                result['distance'] = float(dist)
                results.append(result)

        return results

    def clear_history(self):
        # Очистка истории
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = []
        self._save_to_disk()

    def _remove_oldest_messages(self, percent=20):
        """Удаляет самые старые сообщения"""
        num_to_remove = int(len(self.metadata) * percent / 100)
        if num_to_remove < 1:
            num_to_remove = 1

        # Удаляем из метаданных
        self.metadata = self.metadata[num_to_remove:]

        # Перестраиваем индекс FAISS
        self._rebuild_index()

        # Сохраняем изменения
        self._save_to_disk()

    def _rebuild_index(self):
        """Полностью перестраивает индекс FAISS из текущих метаданных"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        if self.metadata:
            # Собираем все эмбеддинги
            embeddings = []
            for msg in self.metadata:
                embedding = self.embedding_model.encode(msg['message'])
                embeddings.append(embedding)

            # Добавляем в индекс
            embeddings = np.array(embeddings).astype('float32')
            self.index.add(embeddings)

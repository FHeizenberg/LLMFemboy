import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime
import json
import os


class VectorChatHistory:
    def __init__(self, embedding_model_name='sentence-transformers/all-MPNet-base-v2',
                 index_file='chat_index.faiss', meta_file='chat_meta.json',
                 max_messages=150, nlist=150):
        # Initialize the embedding model
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Use an IVF index for better performance on large datasets.
        self.nlist = nlist
        quantizer = faiss.IndexFlatL2(self.embedding_dim)
        self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.nlist, faiss.METRIC_L2)

        self.metadata = []
        self.index_file = index_file
        self.meta_file = meta_file
        self.max_messages = max_messages

        # Load any saved index and metadata if available
        self._load_from_disk()

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
        # Compute the embedding once and cache it in metadata
        embedding = self.embedding_model.encode(message)
        embedding = np.array(embedding, dtype='float32')

        # Remove oldest messages periodically when max_messages is reached.
        if (len(self.metadata) >= self.max_messages) and (len(self.metadata) % 15 == 0):
            self._remove_oldest_messages(percent=20)

        # Append metadata with cached embedding (convert to list for JSON serialization)
        self.metadata.append({
            'role': role,
            'message': message,
            'timestamp': str(datetime.now()),
            'embedding': embedding.tolist()
        })

        # If the index is not trained and enough data is available, train it.
        if not self.index.is_trained:
            if len(self.metadata) >= self.nlist:
                embeddings = np.array([np.array(msg['embedding'], dtype='float32') for msg in self.metadata])
                self.index.train(embeddings)
                self.index.add(embeddings)
        else:
            # Add the new embedding to the already trained index.
            self.index.add(np.array([embedding]))

        self._save_to_disk()

    def search_similar_messages(self, query, k=2):
        # Generate an embedding for the query.
        query_embedding = self.embedding_model.encode(query)
        query_embedding = np.array([query_embedding], dtype='float32')

        # Perform k-nearest neighbor search.
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if 0 <= idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['distance'] = float(dist)
                results.append(result)
        return results

    def clear_history(self):
        quantizer = faiss.IndexFlatL2(self.embedding_dim)
        self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.nlist, faiss.METRIC_L2)
        self.metadata = []
        self._save_to_disk()

    def _remove_oldest_messages(self, percent=20):
        num_to_remove = max(1, int(len(self.metadata) * percent / 100))
        self.metadata = self.metadata[num_to_remove:]
        self._rebuild_index()
        self._save_to_disk()

    def _rebuild_index(self):
        quantizer = faiss.IndexFlatL2(self.embedding_dim)
        self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, self.nlist, faiss.METRIC_L2)
        if self.metadata:
            embeddings = np.array([np.array(msg['embedding'], dtype='float32') for msg in self.metadata])
            if len(self.metadata) >= self.nlist:
                self.index.train(embeddings)
            self.index.add(embeddings)

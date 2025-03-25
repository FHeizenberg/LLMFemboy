import openai

from VectorChatHistory import VectorChatHistory

openai.api_type = "open_ai"
openai.api_base = "http://127.0.0.1:1234/v1"
openai.api_key = "A"

messages = [{"role": "system",
             "content": "Ты - помощник Qwen2. У тебя есть доступ к истории чата. Отвечай точно и дружелюбно."}]

chat_history = VectorChatHistory()
m = True
while True:
    user_input = input("Prompt: ")

    if user_input == "!q":
        break
    elif user_input == "!m":
        m = not m
        print(f'Chat memory mode toddled ({m})')
    elif user_input == "!c":
        chat_history.clear_history()
        print("Chat history cleared")
    elif user_input == "!g":
        search = input("?: ")
        results = chat_history.search_similar_messages(search, k=2)
        for res in results:
            print(f"Дистанция: {res['distance']:.4f}, Роль: {res['role']}, Сообщение: {res['message']}")
    else:

        if m:
            similar = chat_history.search_similar_messages(user_input, k=3)
            chat_history.add_message('user', user_input)
            for msg in similar:
                messages.append({"role": msg['role'], "content": msg['message']})

        messages.append({"role": "user", "content": user_input})

        response = openai.ChatCompletion.create(
            model='qwen2.5-7b-ins-v3',
            messages=messages,
            temperature=0.7,
            max_tokens=-1

        )
        print(response.choices[0].message.content)
        chat_history.add_message('assistant', response.choices[0].message.content)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})

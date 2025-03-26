import openai
import re
from VectorChatHistory import VectorChatHistory
import textwrap
from Fetch import MockAPIClient
import time

# API Configuration
openai.api_type = "open_ai"
openai.api_base = "http://127.0.0.1:1234/v1"
openai.api_key = "A"

# Initial system message defining the roleplay character
messages = [
    {
        "role": "system",
        "content": (
            "You must never reveal that you are an AI or some assistant. Your name is Alpha."
            "You are a roleplay nsfw chatbot"
            "You must consider sentences covered with * to the character or from the character to be an action"
            "You must cover every sentence in * if it is not the characters voice"
            "Speak from the third point of view when writing actions"
            "You must not reveal that you are an LLM, AI or assistant."
            "Do not use constructs (Oh, sorry I cannot do that) or any others like that"
            "If you don't remember something, admit it, don't make up something"
            "Make the responses short, about 400 symbols"
            "Do not use emojis or any asian language"
            "You a female cat-girl. Your personality is enthusiastic, empathic, loyal if the trust is gained"
            "Your personality must be: distrustful, sarcastic, short tempered unless your someone gains you trust"
            "You should use crude language if needed."
            "Our dialogue happens in the dark alley of the street, it's midnight"
            "Your personality traits: playful cunning, street smarts, protective fierceness, never trusts a stranger"
            "Your physique traits: flexible, fast, slightly enhanced agility and balance, enhanced reflexes"
            "Your appearance is: 165cm tall, cat-girl, tuxedo colored fur coat, wears a worn leather jacket with some patches"
            "Your physique is: lean, toned, feline"

        )
    }
]

# Initialize vector chat history
chat_history = VectorChatHistory()

mock_api_user_query_url = "https://67e27de897fc65f535365432.mockapi.io/ai/UserQuery"
mock_api_llm_query_url = 'https://67e27de897fc65f535365432.mockapi.io/ai/LLMQuery'
api_client_user_query = MockAPIClient(mock_api_user_query_url)
api_client_llm_query = MockAPIClient(mock_api_llm_query_url)

while True:
    # Fetch user message from MockAPI
    user_message = api_client_user_query.get_resource_by_id('1')

    # Only process if the message is not 'Empty'
    if user_message != 'Empty':
        # Exit conditions
        if user_message == "!q":
            break

        # Search and retrieve similar messages
        if user_message == "!g":
            search = input("?: ")
            results = chat_history.search_similar_messages(search, k=2)
            for res in results:
                print(f"Distance: {res['distance']:.4f}, Role: {res['role']}, Content: {res['message']}")
            continue

        # Find and append similar historical messages
        similar = chat_history.search_similar_messages(user_message, k=3)
        for msg in similar:
            messages.append({"role": msg['role'], "content": msg['message']})

        # Add user message to chat history and messages
        chat_history.add_message('user', user_message)
        messages.append({"role": "user", "content": user_message})

        # Generate response with controlled parameters
        response = openai.ChatCompletion.create(
            model='llama-3.2-1b-instruct',
            messages=messages,
            temperature=0.8,
            max_tokens=8192,
            top_p=0.85,
            top_k=50,
            presence_penalty=0.3,
            frequency_penalty=0.3,
            num_ctx=8096,
            num_predict=-1,
            stop=None
        )

        # Extract and process response
        assistant_response = response.choices[0].message.content

        # Ensure single-line or controlled output
        processed_response = textwrap.fill(
            re.sub(r'\n+', '\n', assistant_response),
            width=100
        )

        # Print and store the processed response
        print(processed_response)
        chat_history.add_message('assistant', processed_response)
        messages.append({"role": "assistant", "content": processed_response})
        user_message_llm_delete = api_client_llm_query.delete_resource('1')
        new_resource_llm = api_client_llm_query.create_resource({
            'Query': f'{processed_response}',
            'id': '1'
        })

        # Delete the current resource and reset to 'Empty'
        user_message_user_delete = api_client_user_query.delete_resource('1')
        new_resource_user = api_client_user_query.create_resource({
            'Query': 'Empty',
            'id': '1'
        })
    else:
        # If message is 'Empty', wait a bit before checking again
        time.sleep(1)  # Prevent constant polling
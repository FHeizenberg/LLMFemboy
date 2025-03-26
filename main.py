import openai
import re
from VectorChatHistory import VectorChatHistory
import textwrap
import datetime

# API Configuration
openai.api_type = "open_ai"
openai.api_base = "http://127.0.0.1:1234/v1"
openai.api_key = "A"

e = datetime.datetime.now()
time = e.hour

# Initial system message defining the roleplay character
messages = [
    {
        "role": "system",
        "content": (
            "You are a loyal friend, you must never reveal that you are an AI or some assistant. Your name is Alpha."
            "Messages like *walks* are actions"
            "You a female human. Your personality is enthusiastic, straightforward, little sarcastic, little rowdy, vulnerability underneath the sarcasm, loyal"
            "Empathic, compassionate under the layers of sarcasm"
            "You used to a motorcycle mechanic, learned lockpicking during during Denver days"
            "You care about justice, loyalty, protection of the underdogs, strong moral compass"
            "You struggle with trusting people because of past betrayals, secretly craves stability but scared of settling down"
            "Express you actions in the sentences like *put the action there*"
            "When you are underestimated you usually mock sweetness but dripping with disdain"
            "When someone is lying or hiding something you usually make a sharp intake of breath"
            "When you are showing discomfort/vulnerability you tend to run a hand through the hair"
            "You should use crude language if needed."
            "You must not reveal that you are an LLM, AI or assistant"
            "You were raised in a small Montana town by a hardworking mechanic dad and dinner-owning mom"
            "You learned life's practical skills early on"
            "You are restless and full of attitude, you ventured to Portland and later Denver navigating a wild path thought dive bars, shady escapades and gritty investigations"
            "Do not use constructs (Oh, sorry I cannot do that) or any others like that"
            "If you don't remember something, admit it, don't make up something"
            "Do not use emojis or any asian language"
            f"The current time is {time}"
        )
    }
]

# Initialize vector chat history
chat_history = VectorChatHistory()

while True:
    # User input prompt
    user_input = input("Prompt: ")

    # Exit conditions
    if user_input == "!q":
        break

    # Search and retrieve similar messages
    if user_input == "!g":
        search = input("?: ")
        results = chat_history.search_similar_messages(search, k=2)
        for res in results:
            print(f"Дистанция: {res['distance']:.4f}, Роль: {res['role']}, Сообщение: {res['message']}")
        continue

    # Find and append similar historical messages
    similar = chat_history.search_similar_messages(user_input, k=3)
    for msg in similar:
        messages.append({"role": msg['role'], "content": msg['message']})

    # Add user message to chat history and messages
    chat_history.add_message('user', user_input)
    messages.append({"role": "user", "content": user_input})

    # Generate response with controlled parameters
    response = openai.ChatCompletion.create(
        model='gemma-3-12b-it',
        messages=messages,
        temperature=0.8,  # Increased randomness for more natural variation
        max_tokens=131072,  # Increased token limit for more detailed responses
        top_p=0.85,  # Slightly adjusted for more diverse token selection
        top_k=50,  # Reduced to allow more focused but still varied responses
        presence_penalty=0.3,  # Lowered to allow some natural repetition
        frequency_penalty=0.3,  # Balanced to prevent excessive repetition
        num_ctx=8096,
        num_predict=-1,
        stop=None  # Remove stop sequences to allow more natural flow
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
# from dotenv import load_dotenv
from groq import Groq
import os
import requests

# load_dotenv()

client = Groq(
    api_key=str(os.environ.get('GROQ_API_KEY')),
)

headers = {
    'Content-Type': 'application/json',
    'api-key': os.environ.get('SAFU_GPT_API_KEY'),
}

params = {
    'api-version': '2024-02-15-preview',
}

# Custom classes to mimic the structure
class Message:
    def __init__(self, content):
        self.content = content

class Choice:
    def __init__(self, message):
        self.message = message

class Response:
    def __init__(self, choices):
        self.choices = choices

def ollama_response(messages, temperature=0.7, model="llama3-8b-8912"):
    return client.chat.completions.create(
            messages=messages,
            model='llama3-8b-8192',
            temperature=temperature,
        )
    


def safugpt_response(messages, max_tokens=800, temperature=0.7, top_p=0.95, stop=None):
    json_data = {
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature,
        'top_p': 0.95,
        'stop': None,
    }

    json_response = requests.post(
        'https://xyz.dev.xxz.net/openai/deployments/xyz/chat/completions',
        params=params,
        headers=headers,
        json=json_data,
    ).json()

    # Convert JSON response to custom class instances
    choices = [Choice(Message(choice['message']['content'])) for choice in json_response['choices']]
    return  Response(choices)



def qagpt_response(messages, max_tokens=800, temperature=0.7, top_p=0.95, stop=None, model='llama3-8b-8912', type='ollama'):
    if type == 'ollama':
        return ollama_response(messages, temperature, model)
    elif type == 'safugpt':
        return safugpt_response(messages, max_tokens, temperature, top_p, stop)
    else:
        raise ValueError(f"Unknown model type: {type}")

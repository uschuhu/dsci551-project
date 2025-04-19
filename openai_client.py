from openai import OpenAI
from utils import load_config
# Load API key
config = load_config()

CHATGPT_API_KEY = config["CHATGPT_API_KEY"]
client = OpenAI(api_key=CHATGPT_API_KEY)

def chat(messages, temperature=0, max_tokens=200):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content
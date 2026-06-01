import os
from dotenv import load_dotenv
load_dotenv()

def get_client():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY not set. Please add it in Settings.")
    from groq import Groq
    return Groq(api_key=api_key)

def chat(messages: list, max_tokens: int = 1500, temperature: float = 0.6) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content
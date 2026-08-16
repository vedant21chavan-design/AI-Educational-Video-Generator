import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def generate_content(prompt: str) -> str:

    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=data,
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    return result["response"]
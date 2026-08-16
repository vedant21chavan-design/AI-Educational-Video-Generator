import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2",
    "prompt": "Explain photosynthesis in two simple sentences.",
    "stream": False
}


response = requests.post(
    OLLAMA_URL,
    json=data,
    timeout=120
)


response.raise_for_status()

result = response.json()

print("\nLLAMA RESPONSE:\n")
print(result["response"])
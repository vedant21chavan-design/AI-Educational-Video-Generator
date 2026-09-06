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

    # 60s was tuned for GPU inference. Running on CPU (e.g. as a fallback
    # when the GPU/driver can't run Ollama) is much slower, especially with
    # longer prompts, so give it more headroom before calling it a timeout.
    response = requests.post(
        OLLAMA_URL,
        json=data,
        timeout=180
    )

    response.raise_for_status()

    result = response.json()

    return result["response"]
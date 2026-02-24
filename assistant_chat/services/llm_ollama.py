import json

import requests

# URL per defecte on Ollama escolta les peticions a la teva màquina
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"  # El model que hem descarregat


def generate(prompt: str) -> str:
    """
    Envia un prompt al model d'Ollama i retorna la resposta textual.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,  # De moment volem la resposta d'un sol cop
        "options": {
            "temperature": 0.3  # Baixem la creativitat per evitar al·lucinacions
        },
    }

    # Fem la petició HTTP POST al servei local d'Ollama
    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()

    return data.get("response", "").strip()

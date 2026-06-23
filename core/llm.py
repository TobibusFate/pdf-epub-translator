import requests
import json

OLLAMA_URL = "http://localhost:11434"

def check_ollama():
    """Verifica que Ollama esté corriendo y retorna los modelos disponibles."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json()["models"]]
        return models
    except:
        return None

def check_hardware():
    """Detecta el hardware disponible de forma informativa."""
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return f"NVIDIA - {name} ({vram:.1f} GB VRAM)"
        else:
            return "CPU only"
    except:
        return "CPU only"

def translate_chunk(text, target_lang, model):
    """Manda un chunk de texto a Ollama y retorna la traducción."""
    prompt = f"""Translate the following text to {target_lang}.
Rules:
- Preserve all formatting, line breaks, and structure
- Do not translate code, commands, or technical terms in backticks
- Do not add explanations, just return the translated text

Text to translate:
{text}"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    return response.json()["response"].strip()
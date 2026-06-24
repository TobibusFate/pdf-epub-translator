import requests
import json

OLLAMA_URL = "http://localhost:11434"

# Modelos ordenados de mayor a menor calidad
MODEL_PRIORITY = [
    ("qwen2.5:32b", 20),  # requiere ~20GB VRAM
    ("qwen2.5:14b", 10),  # requiere ~10GB VRAM
    ("qwen2.5:7b",   5),  # requiere ~5GB VRAM
    ("qwen2.5:3b",   3),  # requiere ~3GB VRAM
]

def check_ollama():
    """Verifica que Ollama esté corriendo y retorna los modelos disponibles."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json()["models"]]
        return models
    except:
        return None

def get_vram_gb():
    """Detecta la VRAM disponible en GB. Retorna 0 si no hay GPU."""
    try:
        import torch
        if torch.cuda.is_available():
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return vram
        return 0
    except:
        return 0

def check_hardware():
    """Detecta el hardware disponible de forma informativa."""
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram = get_vram_gb()
            return f"NVIDIA - {name} ({vram:.1f} GB VRAM)"
        else:
            return "CPU only"
    except:
        return "CPU only"

def get_best_model(available_models):
    """
    Elige automáticamente el mejor modelo disponible
    según la VRAM detectada.
    """
    vram = get_vram_gb()
    print(f"   VRAM detectada: {vram:.1f} GB")

    # Filtrar modelos que entran en la VRAM disponible
    fitting_models = [
        (name, req) for name, req in MODEL_PRIORITY
        if name in available_models and (vram == 0 or vram >= req)
    ]

    if fitting_models:
        # El primero es el mejor que entra
        chosen = fitting_models[0][0]
        return chosen, f"seleccionado automáticamente ({vram:.1f}GB VRAM disponible)"

    # Ninguno entra perfectamente, usar el más liviano disponible
    for name, _ in reversed(MODEL_PRIORITY):
        if name in available_models:
            return name, "seleccionado por ser el más liviano disponible"

    if available_models:
        return available_models[0], "único modelo disponible"

    return None, "ningún modelo encontrado"

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
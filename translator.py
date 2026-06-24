import argparse
import sys
from pathlib import Path
from tqdm import tqdm

from core.llm import check_ollama, check_hardware, translate_chunk, get_best_model
from core.cache import TranslationCache
from core.chunker import chunk_text, chunk_by_pages, chunk_by_chapters
from extractors.pdf import extract_pdf, get_pdf_info
from extractors.epub import extract_epub, get_epub_info
from builders.pdf import build_pdf, get_output_path
from builders.epub import build_epub


SUPPORTED_LANGS = {
    "es": "Spanish",
    "en": "English",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "zh": "Chinese",
    "ja": "Japanese",
}


def print_header():
    print("\n" + "="*50)
    print("  PDF/EPUB Translator - Local LLM")
    print("="*50)


def check_system(model=None):
    """Verifica hardware y Ollama, elige modelo automáticamente si no se especifica."""
    print(f"\n🖥️  Hardware: {check_hardware()}")

    models = check_ollama()
    if models is None:
        print("❌ Ollama no está corriendo.")
        print("   Inicialo con: ollama serve")
        sys.exit(1)

    print(f"✅ Ollama activo | Modelos disponibles: {', '.join(models)}")

    # Si no se especificó modelo, elegir automáticamente
    if model is None or model == "auto":
        model, reason = get_best_model(models)
        if model is None:
            print("❌ No hay modelos descargados en Ollama.")
            print("   Descargá uno con: ollama pull qwen2.5:7b")
            sys.exit(1)
        print(f"✅ Modelo '{model}' {reason}\n")
    else:
        if model not in models:
            print(f"❌ Modelo '{model}' no encontrado.")
            print(f"   Descargalo con: ollama pull {model}")
            sys.exit(1)
        print(f"✅ Modelo '{model}' listo\n")

    return model


def translate_pdf(file_path, target_lang, model):
    """Pipeline completo de traducción para PDF."""
    info = get_pdf_info(file_path)
    print(f"📄 Archivo : {info['file']}")
    print(f"📑 Páginas : {info['pages']}")
    print(f"📝 Título  : {info['title']}")
    print(f"🌐 Idioma  : {SUPPORTED_LANGS[target_lang]}\n")
    
    cache = TranslationCache(file_path, target_lang)
    print(f"💾 Caché   : {cache.stats()} chunks ya traducidos\n")
    
    print("⏳ Extrayendo contenido del PDF...")
    pages = extract_pdf(file_path)
    
    translated_pages = []
    
    with tqdm(total=len(pages), desc="Traduciendo", unit="pág") as pbar:
        for page in pages:
            translated_blocks = []
            
            for block in page["blocks"]:
                if block["type"] != 0:  # saltar bloques de imagen
                    translated_blocks.append(block)
                    continue
                
                text = block["text"].strip()
                if not text:
                    translated_blocks.append(block)
                    continue
                
                # Verificar caché
                cached = cache.get(text)
                if cached:
                    translated_text = cached
                else:
                    chunks = chunk_text(text)
                    translated_parts = []
                    for chunk in chunks:
                        translation = translate_chunk(
                            chunk,
                            SUPPORTED_LANGS[target_lang],
                            model
                        )
                        translated_parts.append(translation)
                    translated_text = "\n".join(translated_parts)
                    cache.set(text, translated_text)
                
                block_copy = block.copy()
                block_copy["translated_text"] = translated_text
                translated_blocks.append(block_copy)
            
            translated_pages.append({
                "page_num": page["page_num"],
                "translated_blocks": translated_blocks,
                "images": page["images"]
            })
            pbar.update(1)
    
    output_path = get_output_path(file_path, target_lang)
    print(f"\n🔨 Construyendo PDF traducido...")
    build_pdf(file_path, translated_pages, output_path)
    print(f"✅ Listo: {output_path}")


def translate_epub(file_path, target_lang, model):
    """Pipeline completo de traducción para EPUB."""
    info = get_epub_info(file_path)
    print(f"📚 Archivo   : {info['file']}")
    print(f"📑 Capítulos : {info['chapters']}")
    print(f"📝 Título    : {info['title']}")
    print(f"✍️  Autor     : {info['author']}")
    print(f"🌐 Idioma    : {SUPPORTED_LANGS[target_lang]}\n")
    
    cache = TranslationCache(file_path, target_lang)
    print(f"💾 Caché     : {cache.stats()} chunks ya traducidos\n")
    
    print("⏳ Extrayendo contenido del EPUB...")
    epub_data = extract_epub(file_path)
    chapters = epub_data["chapters"]
    
    translated_chapters = []
    
    with tqdm(total=len(chapters), desc="Traduciendo", unit="cap") as pbar:
        for chapter in chapters:
            text = chapter["text"].strip()
            if not text:
                translated_chapters.append({
                    "original": chapter,
                    "translated_text": ""
                })
                pbar.update(1)
                continue
            
            # Verificar caché
            cached = cache.get(text)
            if cached:
                translated_text = cached
            else:
                chunks = chunk_text(text, max_chars=3000)
                translated_parts = []
                for chunk in chunks:
                    translation = translate_chunk(
                        chunk,
                        SUPPORTED_LANGS[target_lang],
                        model
                    )
                    translated_parts.append(translation)
                translated_text = "\n\n".join(translated_parts)
                cache.set(text, translated_text)
            
            translated_chapters.append({
                "original": chapter,
                "translated_text": translated_text
            })
            pbar.update(1)
    
    output_path = Path(file_path).parent / f"{epub_data['title']}_{target_lang}.epub"
    print(f"\n🔨 Construyendo EPUB traducido...")
    build_epub(epub_data, translated_chapters, target_lang, output_path)
    print(f"✅ Listo: {output_path}")


def main():
    print_header()
    
    parser = argparse.ArgumentParser(
        description="Traduce PDFs y EPUBs usando un LLM local via Ollama"
    )
    parser.add_argument("file", help="Archivo PDF o EPUB a traducir")
    parser.add_argument(
        "--lang", default="es",
        choices=SUPPORTED_LANGS.keys(),
        help="Idioma destino (default: es)"
    )
    parser.add_argument(
    "--model", default="auto",
    help="Modelo de Ollama a usar (default: auto)"
    )
    
    args = parser.parse_args()
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        sys.exit(1)
    
    model = check_system(args.model)
    
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        translate_pdf(str(file_path), args.lang, model)
    elif ext == ".epub":
        translate_epub(str(file_path), args.lang, model)
    else:
        print(f"❌ Formato no soportado: {ext}")
        print("   Formatos soportados: .pdf, .epub")
        sys.exit(1)


if __name__ == "__main__":
    main()
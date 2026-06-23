from ebooklib import epub
from pathlib import Path


def build_epub(original_data, translated_chapters, target_lang, output_path=None):
    """
    Reconstruye el EPUB con los capítulos traducidos.
    Preserva imágenes, metadata y estructura original.
    """
    src_title = original_data["title"]
    
    if output_path is None:
        output_path = Path(f"{src_title}_{target_lang}.epub")
    
    book = epub.EpubBook()
    
    # Metadata
    book.set_title(f"{src_title} ({target_lang})")
    book.set_language(target_lang)
    book.add_author(original_data["author"])
    
    # Reimportar imágenes originales
    for name, img_data in original_data["images"].items():
        img_item = epub.EpubItem(
            uid=name,
            file_name=name,
            media_type=img_data["media_type"],
            content=img_data["bytes"]
        )
        book.add_item(img_item)
    
    # Construir capítulos traducidos
    epub_chapters = []
    spine = ["nav"]
    
    for i, chapter_data in enumerate(translated_chapters):
        original = chapter_data["original"]
        translated_text = chapter_data["translated_text"]
        
        # Convertir texto traducido a HTML simple
        html_content = _text_to_html(translated_text, original["name"])
        
        chapter = epub.EpubHtml(
            title=original["name"],
            file_name=original["name"],
            lang=target_lang
        )
        chapter.content = html_content
        
        book.add_item(chapter)
        epub_chapters.append(chapter)
        spine.append(chapter)
    
    # Estructura del libro
    book.toc = epub_chapters
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # CSS básico para legibilidad
    css = epub.EpubItem(
        uid="style",
        file_name="style.css",
        media_type="text/css",
        content=_default_css()
    )
    book.add_item(css)
    
    epub.write_epub(str(output_path), book)
    return output_path


def _text_to_html(text, title):
    """Convierte texto plano traducido a HTML para el EPUB."""
    paragraphs = text.split("\n\n")
    html_parts = [f"<h1>{title}</h1>"]
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Detectar si parece encabezado (línea corta sin punto final)
        if len(para) < 80 and not para.endswith("."):
            html_parts.append(f"<h2>{para}</h2>")
        else:
            # Preservar saltos de línea dentro del párrafo
            lines = para.replace("\n", "<br/>")
            html_parts.append(f"<p>{lines}</p>")
    
    return f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
    {"".join(html_parts)}
</body>
</html>"""


def _default_css():
    """CSS básico para buena legibilidad."""
    return """
body {
    font-family: Georgia, serif;
    font-size: 1em;
    line-height: 1.6;
    margin: 2em;
    color: #1a1a1a;
}
h1 {
    font-size: 1.5em;
    margin-bottom: 1em;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0.3em;
}
h2 {
    font-size: 1.2em;
    margin-top: 1.5em;
}
p {
    margin: 0.8em 0;
    text-align: justify;
}
"""
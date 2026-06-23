def chunk_text(text, max_chars=2000):
    """
    Divide un texto largo en chunks respetando párrafos.
    No corta a la mitad de una oración.
    """
    if len(text) <= max_chars:
        return [text]
    
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # Si el párrafo solo ya supera el límite, lo dividimos por oraciones
        if len(paragraph) > max_chars:
            sentences = paragraph.replace(". ", ".\n").split("\n")
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > max_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence
        else:
            if len(current_chunk) + len(paragraph) > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n" + paragraph
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def chunk_by_pages(pages):
    """
    Para PDFs: retorna una lista de (numero_pagina, texto).
    Cada página es un chunk independiente para preservar el layout.
    """
    return [(i + 1, page) for i, page in enumerate(pages) if page.strip()]


def chunk_by_chapters(chapters):
    """
    Para EPUBs: retorna una lista de (titulo_capitulo, texto).
    Cada capítulo es un chunk independiente.
    """
    return [(title, content) for title, content in chapters if content.strip()]
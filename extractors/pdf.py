import fitz  # PyMuPDF
from pathlib import Path


def extract_pdf(file_path):
    """
    Extrae texto e imágenes de un PDF manteniendo estructura por páginas.
    Retorna una lista de dicts con la info de cada página.
    """
    path = Path(file_path)
    doc = fitz.open(str(path))
    
    pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extraer texto con layout preservado
        text = page.get_text("text")
        
        # Extraer bloques con posición (para reconstrucción)
        blocks = page.get_text("blocks")
        # Cada block: (x0, y0, x1, y1, text, block_no, block_type)
        text_blocks = [
            {
                "x0": b[0], "y0": b[1],
                "x1": b[2], "y1": b[3],
                "text": b[4],
                "block_no": b[5],
                "type": b[6]  # 0=texto, 1=imagen
            }
            for b in blocks
        ]
        
        # Extraer imágenes de la página
        images = []
        img_list = page.get_images(full=True)
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            images.append({
                "index": img_index,
                "xref": xref,
                "bytes": base_image["image"],
                "ext": base_image["ext"],
                "width": base_image["width"],
                "height": base_image["height"]
            })
        
        pages.append({
            "page_num": page_num + 1,
            "width": page.rect.width,
            "height": page.rect.height,
            "text": text,
            "blocks": text_blocks,
            "images": images
        })
    
    doc.close()
    return pages


def get_pdf_info(file_path):
    """Retorna información básica del PDF."""
    doc = fitz.open(str(file_path))
    info = {
        "pages": len(doc),
        "title": doc.metadata.get("title", "Sin título"),
        "author": doc.metadata.get("author", "Desconocido"),
        "file": Path(file_path).name
    }
    doc.close()
    return info
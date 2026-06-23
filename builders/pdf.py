import fitz  # PyMuPDF
from pathlib import Path


def build_pdf(original_path, translated_pages, output_path=None):
    """
    Reconstruye el PDF reemplazando el texto original con la traducción.
    Preserva imágenes, layout y formato original.
    """
    src_path = Path(original_path)
    if output_path is None:
        output_path = src_path.parent / f"{src_path.stem}_translated.pdf"
    
    doc = fitz.open(str(src_path))
    
    for page_data in translated_pages:
        page_num = page_data["page_num"] - 1
        page = doc[page_num]
        
        if not page_data.get("translated_blocks"):
            continue
        
        for block in page_data["translated_blocks"]:
            if not block.get("translated_text"):
                continue
            
            # Área del bloque original
            rect = fitz.Rect(
                block["x0"], block["y0"],
                block["x1"], block["y1"]
            )
            
            # Tapar el texto original con un rectángulo del color de fondo
            page.draw_rect(rect, color=None, fill=(1, 1, 1))
            
            # Calcular tamaño de fuente que encaje
            font_size = _fit_font_size(
                block["translated_text"],
                rect,
                start_size=10
            )
            
            # Escribir el texto traducido
            page.insert_textbox(
                rect,
                block["translated_text"],
                fontsize=font_size,
                fontname="helv",
                color=(0, 0, 0),
                align=0  # izquierda
            )
    
    doc.save(str(output_path))
    doc.close()
    
    return output_path


def _fit_font_size(text, rect, start_size=10):
    """
    Reduce el tamaño de fuente hasta que el texto entre en el rectángulo.
    """
    width = rect.x1 - rect.x0
    height = rect.y1 - rect.y0
    
    # Estimación simple: chars por línea y líneas disponibles
    for size in range(start_size, 5, -1):
        chars_per_line = int(width / (size * 0.5))
        lines_available = int(height / (size * 1.2))
        chars_available = chars_per_line * lines_available
        
        if len(text) <= chars_available:
            return size
    
    return 6  # mínimo absoluto


def get_output_path(original_path, target_lang):
    """Genera la ruta del archivo de salida."""
    src = Path(original_path)
    return src.parent / f"{src.stem}_{target_lang}.pdf"
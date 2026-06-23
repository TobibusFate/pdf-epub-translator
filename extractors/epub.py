import ebooklib
from ebooklib import epub
from html.parser import HTMLParser
from pathlib import Path


class HTMLTextExtractor(HTMLParser):
    """Extrae texto limpio de HTML preservando saltos de línea."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {"script", "style"}
        self.current_skip = None
        self.block_tags = {"p", "h1", "h2", "h3", "h4", "h5", "h6", 
                          "li", "tr", "div", "br"}
    
    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.current_skip = tag
        if tag in self.block_tags:
            self.text_parts.append("\n")
    
    def handle_endtag(self, tag):
        if tag == self.current_skip:
            self.current_skip = None
        if tag in self.block_tags:
            self.text_parts.append("\n")
    
    def handle_data(self, data):
        if self.current_skip is None:
            self.text_parts.append(data)
    
    def get_text(self):
        return "".join(self.text_parts).strip()


def html_to_text(html_content):
    """Convierte HTML de un capítulo a texto limpio."""
    parser = HTMLTextExtractor()
    parser.feed(html_content)
    return parser.get_text()


def extract_epub(file_path):
    """
    Extrae capítulos e imágenes de un EPUB.
    Retorna una lista de dicts con la info de cada capítulo.
    """
    path = Path(file_path)
    book = epub.read_epub(str(path))
    
    chapters = []
    images = {}
    
    # Extraer imágenes
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_IMAGE:
            images[item.get_name()] = {
                "name": item.get_name(),
                "bytes": item.get_content(),
                "media_type": item.media_type
            }
    
    # Extraer capítulos en orden
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html_content = item.get_content().decode("utf-8", errors="ignore")
        text = html_to_text(html_content)
        
        if not text.strip():
            continue
        
        chapters.append({
            "id": item.get_id(),
            "name": item.get_name(),
            "html": html_content,
            "text": text
        })
    
    return {
        "title": book.title or path.stem,
        "author": ", ".join([str(a) for a in book.authors]) if book.authors else "Desconocido",
        "chapters": chapters,
        "images": images,
        "language": book.language or "en"
    }


def get_epub_info(file_path):
    """Retorna información básica del EPUB."""
    book = epub.read_epub(str(file_path))
    path = Path(file_path)
    return {
        "title": book.title or path.stem,
        "author": ", ".join([str(a) for a in book.authors]) if book.authors else "Desconocido",
        "chapters": len(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))),
        "file": path.name
    }
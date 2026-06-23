import json
import hashlib
from pathlib import Path

class TranslationCache:
    """Guarda el progreso de traducción para no retraducir si se corta el proceso."""
    
    def __init__(self, source_file, target_lang):
        source_path = Path(source_file)
        cache_dir = source_path.parent / ".cache"
        cache_dir.mkdir(exist_ok=True)
        
        cache_name = f"{source_path.stem}_{target_lang}.json"
        self.cache_file = cache_dir / cache_name
        self.data = self._load()
    
    def _load(self):
        """Carga el caché existente o crea uno nuevo."""
        if self.cache_file.exists():
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save(self):
        """Guarda el caché en disco."""
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get(self, text):
        """Retorna la traducción cacheada o None si no existe."""
        key = hashlib.md5(text.encode()).hexdigest()
        return self.data.get(key)
    
    def set(self, text, translation):
        """Guarda una traducción en el caché."""
        key = hashlib.md5(text.encode()).hexdigest()
        self.data[key] = translation
        self._save()
    
    def stats(self):
        """Retorna cuántos chunks ya están traducidos."""
        return len(self.data)
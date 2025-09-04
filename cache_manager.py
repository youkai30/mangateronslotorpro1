# core/cache_manager.py
import os, json, pickle, hashlib, threading, gc
from pathlib import Path
import torch, logging

class ModelCacheManager:
    def __init__(self, cache_dir="./model_cache", max_memory_models=2):
        self.cache_dir = Path(cache_dir); self.cache_dir.mkdir(exist_ok=True)
        self.cache_info_file = self.cache_dir / "cache_info.json"
        self.lock = threading.Lock()
        self.max_memory_models = max_memory_models
        self.memory_cache = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_model_hash(self, model_name, model_config=None):
        key = f"{model_name}_{model_config}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def save_to_disk(self, key, data):
        with self.lock:
            with open(self.cache_dir/f"{key}.pkl", "wb") as f:
                pickle.dump(data, f)
            self._update_cache_info(key)
            self.logger.debug(f"Saved model '{key}' to disk")

    def load_from_disk(self, key):
        path = self.cache_dir/f"{key}.pkl"
        if path.exists():
            self.logger.debug(f"Loading model '{key}' from disk")
            with open(path, "rb") as f:
                return pickle.load(f)
        return None

    def get_model(self, key, loader_func):
        with self.lock:
            if key in self.memory_cache:
                self.logger.debug(f"Loaded '{key}' from memory")
                return self.memory_cache[key]
            data = self.load_from_disk(key)
            if data is not None:
                self.logger.info(f"Loaded '{key}' from disk cache")
                self._add_to_memory(key, data)
                return data
            self.logger.info(f"Cache miss for '{key}', loading model…")
            try:
                data = loader_func()
            except Exception:
                self.logger.exception(f"Failed to load model '{key}'")
                raise
            self.save_to_disk(key, data)
            self._add_to_memory(key, data)
            return data

    def _add_to_memory(self, key, data):
        if len(self.memory_cache) >= self.max_memory_models:
            old = next(iter(self.memory_cache))
            del self.memory_cache[old]
            gc.collect()
            if torch.cuda.is_available(): torch.cuda.empty_cache()
            self.logger.debug(f"Evicted '{old}' from memory cache")
        self.memory_cache[key] = data

    def _update_cache_info(self, key):
        info = {}
        if self.cache_info_file.exists():
            info = json.loads(self.cache_info_file.read_text())
        size = round((self.cache_dir/f"{key}.pkl").stat().st_size/(1024*1024),2)
        info[key] = {"last_used": str(Path().resolve()), "size_mb": size}
        self.cache_info_file.write_text(json.dumps(info, indent=2))

    def cleanup_old_cache(self, days=30):
        import time
        cutoff = time.time() - days*24*3600
        for f in self.cache_dir.glob("*.pkl"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                self.logger.info(f"Removed old cache file {f.name}")
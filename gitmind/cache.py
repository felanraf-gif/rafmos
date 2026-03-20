import time
from typing import Dict, Any, Optional
from threading import Lock


class SimpleCache:
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry['timestamp'] < self.ttl:
                    entry['hits'] += 1
                    return entry['value']
                else:
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any):
        with self._lock:
            if len(self._cache) >= self.max_size:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k]['timestamp']
                )
                del self._cache[oldest_key]
            
            self._cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'hits': 0
            }
    
    def delete(self, key: str):
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict:
        with self._lock:
            total_hits = sum(e['hits'] for e in self._cache.values())
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'total_hits': total_hits,
                'ttl': self.ttl
            }


mr_cache = SimpleCache(max_size=50, ttl=60)

llm_cache = SimpleCache(max_size=100, ttl=3600)


def cache_key(*args) -> str:
    return ':'.join(str(arg) for arg in args)

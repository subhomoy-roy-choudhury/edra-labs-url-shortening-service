import threading

class CacheManager:
    def __init__(self):
        self.cache = {}
    
    def set_cache(self, key, value, timeout):
        self.cache[key] = value
        timer = threading.Timer(timeout, self.delete_cache, args=[key])
        timer.start()

    def delete_cache(self, key):
        if key in self.cache:
            del self.cache[key]
            print(f"Cache for '{key}' deleted.")

    def get_cache(self, key):
        return self.cache.get(key, None)
    
    def keys(self):
        return self.cache.keys()
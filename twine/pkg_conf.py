import json


class PkgConfig(object):

    __cache = None

    def __init__(self, path):
        self.path = path

    def load_cache(self):
        with open(self.path, 'r') as conf:
            PkgConfig.__cache = json.load(conf)
        return PkgConfig.__cache

    def get(self, key):
        cache = PkgConfig.__cache if PkgConfig.__cache else load_cache()
        return cache.get(key)

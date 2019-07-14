from logger import Logger

import os, json
from Crypto.Cipher import AES


class Cache(object):
    handler_cache = {}
    shared_cache = {}
    credentials_cipher = None

    @classmethod
    def set_cache_location(cls, loc):
        Logger.log_trace('Cache location set to %s' % loc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        if os.path.isfile(loc):
            Logger.log_error('The specified cache location must be a folder, not \'%\'' % loc)
            raise Exception()
        cls.cache_location = os.path.join(loc, 'bot_cache.json')

    @classmethod
    def store_cache(cls):
        cache = {'handlers': cls.handler_cache, 'shared': cls.shared_cache}
        with open(cls.cache_location, 'w') as cache_file:
            Logger.log_debug('Writing cache to disk')
            json.dump(cache, cache_file)

    @classmethod
    def load_cache(cls):
        if os.path.exists(cls.cache_location):
            with open(cls.cache_location, 'r') as cache_file:
                Logger.log_debug('Loading cache')
                content = cache_file.read()
                if content:
                    cache = json.loads(content)
                    if ('handlers' not in cache) or ('shared' not in cache):
                        Logger.log_error('Malformed cache, starting with a fresh cache')
                    else:
                        cls.handler_cache = cache['handlers']
                        cls.shared_cache = cache['shared']
        else:
            Logger.log_trace('Cache file does not exist (can be ignored on the initial run)')
            cls.handler_cache = {}
            cls.shared_cache = {}

    @classmethod
    def handler_put_cache(cls, id, key, value):
        if id not in cls.handler_cache:
            cls.handler_cache[id] = {}
        cls.handler_cache[id][key] = value

    @classmethod
    def handler_get_cache(cls, id, key):
        if id not in cls.handler_cache:
            return None
        return cls.handler_cache[id]
        if key in cache:
            return cache[key]
        else:
            return None

    @classmethod
    def set_cipher_pwd(cls, key):
        # Never log the key here
        Logger.log_trace('Creating the cipher for cache encryption')
        cls.credentials_cipher = AES.new(key, AES.MODE_ECB)

    @classmethod
    def shared_put_cache_encrypted(cls, key, value):
        if not cls.credentials_cipher:
            Logger.log_error('No cipher key set for the cache')
            return

        encoded = cls.credentials_cipher.encrypt(cls._add_padding(value))
        cls.shared_put_cache(key, encoded.hex())

    @classmethod
    def shared_put_cache(cls, key, value):
        cls.shared_cache[key] = value

    @classmethod
    def shared_get_cache_encrypted(cls, key):
        if not cls.credentials_cipher:
            Logger.log_error('No cipher key set for the cache')
            return None

        cached = cls.shared_get_cache(key)
        if cached:
            hex_bytes = cls._remove_padding(cls.credentials_cipher.decrypt(bytes.fromhex(cache)))
            return hex_bytes
        else:
            return None

    @classmethod
    def shared_get_cache(cls, key):
        if key in cls.shared_cache:
            return cls.shared_cache[key]
        else:
            return None

    @classmethod
    def _add_padding(cls, text):
        data = text.encode('utf-8')
        length = 16 - (len(data) % 16)
        data += bytes([length])*length
        return data

    @classmethod
    def _remove_padding(cls, data):
        data = data[:-data[-1]]
        return data.decode('utf-8')

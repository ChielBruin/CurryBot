from logger import Logger

import os, json
from Crypto.Cipher import AES


class Cache(object):
    _cache = {}
    _save_cache = {}
    credentials_cipher = None

    @classmethod
    def set_cache_location(cls, loc):
        Logger.log_trace('Cache location set to \'%s\'' % loc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        if os.path.isfile(loc):
            Logger.log_error('The specified cache location must be a folder, not \'%\'' % loc)
            raise Exception()
        cls.cache_location = os.path.join(loc, 'bot_cache.json')

    @classmethod
    def store_cache(cls):
        # Select all the cache entries of which the id is configured to store to disk
        cache = {}
        for cache_entry in cls._cache:
            if cache_entry in cls._save_cache and cls._save_cache[cache_entry] is True:
                cache[cache_entry] = cls._cache[cache_entry]

        # Write the selected parts of the cache to file
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
                    try:
                        cls._cache = json.loads(content)
                    except:
                        print(content)
                        Logger.log_error('Malformed cache, starting with a fresh cache')
                else:
                    Logger.log_info('Cache file appears to be empty')
                    self._cache = {}
        else:
            Logger.log_error('Cache file does not exist (This error can be ignored on the initial run)')
            cls._cache = {}

    @classmethod
    def set_cipher_pwd(cls, key):
        # Never log the key here
        Logger.log_trace('Creating the cipher for cache encryption')
        cls.credentials_cipher = AES.new(key, AES.MODE_ECB)

    @classmethod
    def clear(cls, key):
        cls.put(key, None)

    @classmethod
    def config_entry(cls, key, val):
        cls._save_cache[key] = val

    @classmethod
    def put(cls, keys, value, encrypt=False):
        if encrypt:
            if not cls.credentials_cipher:
                Logger.log_error('No cipher key set for the cache')
                return
            value = cls.credentials_cipher.encrypt(cls._add_padding(value)).hex()

        if isinstance(keys, list):
            cls._put_list(keys, value)
        else:
            cls._put_single(keys, value)

    @classmethod
    def get(cls, keys, decrypt=False):
        if isinstance(keys, list):
            val = cls._get_list(keys)
        else:
            val = cls._get_single(keys)

        if decrypt:
            if not cls.credentials_cipher:
                Logger.log_error('No cipher key set for the cache')
                return None
            return cls._remove_padding(cls.credentials_cipher.decrypt(bytes.fromhex(val)))
        else:
            return val

    @classmethod
    def _put_list(cls, keys, value):
        cache = cls._cache
        for key in keys[:-1]:
            if key not in cache:
                cache[key] = {}
            cache = cache[key]
        cache[-1] = value

    @classmethod
    def _put_single(cls, key, value):
        cache = cls._cache
        cls._cache[key] = value

    @classmethod
    def _get_list(cls, keys):
        cache = cls._cache
        for key in keys:
            if key not in cache:
                return None
            else:
                cache = cache[key]

        return cache

    @classmethod
    def _get_single(cls, key):
        return cls._cache[key]


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

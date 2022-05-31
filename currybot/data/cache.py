from .logger import Logger

import os, json
from Crypto.Cipher import AES


class Cache(object):
    _cache = {}
    _save_cache = {}
    chat_admins = {}
    chat_titles = {}
    standalone_chats = []
    chat_keys = {}
    api_keys = {}
    credentials_cipher = None

    @classmethod
    def migrate(cls, from_id, to_id):
        if from_id in cls.chat_admins:
            cls.chat_admins[to_id] = cls.chat_admins[from_id]
            cls.chat_admins.pop(from_id, None)

        cls.chat_keys.pop(from_id, None)

        if from_id in cls.chat_keys:
            cls.chat_keys[to_id] = cls.chat_keys[from_id]
            cls.chat_keys.pop(from_id, None)

    @classmethod
    def chat_is_standalone(cls, chat_id):
        chat_id = str(chat_id)
        return chat_id in cls.standalone_chats

    @classmethod
    def chat_set_standalone(cls, chat_id, val):
        chat_id = str(chat_id)
        if val:
            if chat_id not in cls.standalone_chats:
                cls.standalone_chats.append(chat_id)
        else:
            if chat_id in cls.standalone_chats:
                cls.standalone_chats = [x for x in cls.standalone_chats if x != chat_id]

    @classmethod
    def set_chat_title(cls, chat_id, title):
        cls.chat_titles[str(chat_id)] = title

    @classmethod
    def get_chat_title(cls, chat_id):
        return cls.chat_titles[str(chat_id)]

    @classmethod
    def list_chat_titles(cls):
        return cls.chat_titles.values()

    @classmethod
    def list_chat_ids(cls):
        return cls.chat_titles.keys()

    @classmethod
    def add_chat_admin(cls, chat_id, admin):
        chat_id = str(chat_id)
        if chat_id in cls.chat_admins:
            chat_admins = cls.chat_admins[chat_id]
            if admin not in chat_admins:
                chat_admins.append(admin)
        else:
            cls.chat_admins[chat_id] = [admin]

    @classmethod
    def is_chat_admin(cls, chat_id, user):
        chat_id = str(chat_id)
        if chat_id in cls.chat_admins:
            return user in cls.chat_admins[chat_id]
        else:
            Logger.log_error('No admin set for chat %s' % chat_id)
            return False


    @classmethod
    def set_cache_location(cls, loc):
        Logger.log_trace('Cache location set to \'%s\'' % loc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        if os.path.isfile(loc):
            Logger.log_error('The specified cache location must be a folder, not \'%s\'' % loc)
            raise Exception()
        cls.cache_location = os.path.join(loc, 'bot_cache.json')
        cls.meta_location  = os.path.join(loc, 'bot_metadata.json')

    @classmethod
    def store_cache(cls):
        # Select all the cache entries of which the id is configured to store to disk
        meta = {
            'admins': cls.chat_admins,
            'titles': cls.chat_titles,
            'keys'  : cls.chat_keys,
            'api'   : cls.api_keys,
            'save'  : cls._save_cache,
            'standalone': cls.standalone_chats
        }
        cache = {}

        for cache_entry in cls._cache:
            if cache_entry in cls._save_cache and cls._save_cache[cache_entry] is True:
                cache[cache_entry] = cls._cache[cache_entry]

        # Write the selected parts of the cache to file
        with open(cls.cache_location, 'w') as cache_file:
            Logger.log_debug('Writing cache to disk')
            json.dump(cache, cache_file)
        with open(cls.meta_location, 'w') as meta_file:
            Logger.log_debug('Writing metadata to disk')
            json.dump(meta, meta_file)

    @classmethod
    def load_cache(cls):
        def try_load_json(filename, type):
            if os.path.exists(filename):
                with open(filename, 'r') as cache_file:
                    Logger.log_debug('Loading %s' % type)
                    content = cache_file.read()
                    if content:
                        try:
                            return json.loads(content)
                        except:
                            Logger.log_error('Malformed %s, starting with a fresh %s file' % type)
                    else:
                        Logger.log_info('%s file appears to be empty' % type)
            else:
                Logger.log_error('%s file does not exist (This error can be ignored on the initial run)' % type)
            return {}


        cls._cache = try_load_json(cls.cache_location, 'cache')
        meta = try_load_json(cls.meta_location, 'metadata')

        cls._save_cache = meta['save']   if 'save'   in meta else {}
        cls.chat_admins = meta['admins'] if 'admins' in meta else {}
        cls.chat_titles = meta['titles'] if 'titles' in meta else {}
        cls.chat_keys   = meta['keys']   if 'keys'   in meta else {}
        cls.api_keys    = meta['api']    if 'api'    in meta else {}
        cls.standalone_chats = meta['standalone'] if 'standalone' in meta else []

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
    def contains(cls, keys):
        if isinstance(keys, list):
            return cls._contains(keys)
        else:
            return cls._contains([keys])

    @classmethod
    def get_admin_chats(self, user_id):
        for chat_id in self.chat_admins:
            if user_id in self.chat_admins[chat_id]:
                yield chat_id

    @classmethod
    def add_chat_key(cls, key, chat_id):
        cls._add_key(cls.chat_keys, key, chat_id)

    @classmethod
    def get_chat_keys(cls, chat_id):
        return cls._get_keys(cls.chat_keys, chat_id)

    @classmethod
    def add_api_key(cls, key, chat_id):
        cls.config_entry(key, True)
        cls._add_key(cls.api_keys, key, chat_id)

    @classmethod
    def get_api_keys(cls, chat_id):
        return cls._get_keys(cls.api_keys, chat_id)

    @classmethod
    def _add_key(cls, dict, key, chat_id):
        chat_id = str(chat_id)
        if chat_id not in dict:
            dict[chat_id] = [key]
        elif key not in dict[chat_id]:
            dict[chat_id].append(key)

    @classmethod
    def _get_keys(cls, dict, chat_id):
        chat_id = str(chat_id)
        if chat_id not in dict:
            return []
        else:
            return dict[chat_id]


    @classmethod
    def _contains(cls, keys):
        cache = cls._cache
        for key in keys:
            if key not in cache:
                return False
            else:
                cache = cache[key]

        return True


    @classmethod
    def _put_list(cls, keys, value):
        cache = cls._cache
        for key in keys[:-1]:
            if key not in cache or cache[key] is None:
                cache[key] = {}
            cache = cache[key]
        cache[keys[-1]] = value

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

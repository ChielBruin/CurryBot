import os, json

from logger import Logger
from messageHandler import MessageHandler


class Config (object):
    chat_admins = {}
    chat_titles = {}
    chat_keys = {}
    api_keys = {}

    @classmethod
    def set_chat_title(cls, chat_id, title):
        cls.chat_titles[str(chat_id)] = title

    @classmethod
    def get_chat_title(cls, chat_id):
        return cls.chat_titles[str(chat_id)]

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
            Logger.log_error('No admin set for chat %d' % chat_id)
            return False

    @classmethod
    def set_config_location(cls, loc):
        Logger.log_trace('Config location set to \'%s\'' % loc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        if os.path.isfile(loc):
            Logger.log_error('The specified config location must be a folder, not \'%\'' % loc)
            raise Exception()
        cls.config_location = os.path.join(loc, 'bot_config.json')

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
    def store_config(cls, bot):
        Logger.log_debug('Serializing config')
        handlers = {}
        for chat_id in bot._chat_message_handlers:
            handlers[chat_id] = {}
            chat_handlers = bot._chat_message_handlers[chat_id]
            for (name, handler) in chat_handlers:
                handlers[chat_id][name] = handler.to_dict()
        print(handlers)

        tick_handlers = {}
        for (name, handler) in bot._tick_handlers:
            tick_handlers[name] = handler.to_dict()
        print(tick_handlers)

        config = {
            'admins': cls.chat_admins,
            'titles': cls.chat_titles,
            'keys'  : cls.chat_keys,
            'api'  : cls.api_keys,
            'handlers': handlers,
            'tick_handlers': tick_handlers
        }
        with open(cls.config_location, 'w') as config_file:
            Logger.log_debug('Writing config to disk')
            json.dump(config, config_file)

    @classmethod
    def load_config(cls, bot):
        if os.path.exists(cls.config_location):
            with open(cls.config_location, 'r') as config_file:
                Logger.log_debug('Loading config')
                content = config_file.read()
                try:
                    config = json.loads(content)
                except json.JSONDecodeError as ex:
                    config = {}
                    Logger.log_error('Malformed config file')

                cls.chat_admins = config['admins'] if 'admins' in config else {}
                cls.chat_titles = config['titles'] if 'titles' in config else {}
                cls.chat_keys   = config['keys']   if 'keys'   in config else {}
                cls.api_keys    = config['api']    if 'api'    in config else {}

                handlers = config['handlers'] if 'handlers' in config else {}
                for chat_id in handlers:
                    chat_handlers = handlers[chat_id]
                    for handler_name in chat_handlers:
                        handler_dict = chat_handlers[handler_name]
                        print(handler_dict)
                        handler = MessageHandler.class_from_dict(handler_dict).from_dict(handler_dict)
                        self.bot.register_message_handler(chat, handler, handler_name)

                handlers = config['tick_handlers'] if 'tick_handlers' in config else {}
                for chat_id in handlers:
                    chat_handlers = handlers[chat_id]
                    for handler_name in chat_handlers:
                        handler_dict = chat_handlers[handler_name]
                        print(handler_dict)
                        handler = MessageHandler.class_from_dict(handler_dict).from_dict(handler_dict)
                        self.bot.register_tick_handler(chat, handler, handler_name)

        else:
            Logger.log_error('Config file does not exist (This error can be ignored on the initial run)')
            cls.chat_admins = {}
            cls.chat_titles = {}
            cls.chat_keys   = {}
            cls.api_keys    = {}

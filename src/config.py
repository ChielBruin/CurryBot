import os, json

from logger import Logger


class Config (object):
    chat_admins = {}
    chat_titles = {}

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
    def store_config(cls):
        config = {
            'admins': cls.chat_admins,
            'titles': cls.chat_titles
        }
        with open(cls.config_location, 'w') as config_file:
            Logger.log_debug('Writing config to disk')
            json.dump(config, config_file)

    @classmethod
    def load_config(cls):
        if os.path.exists(cls.config_location):
            with open(cls.config_location, 'r') as config_file:
                Logger.log_debug('Loading config')
                content = config_file.read()
                if content:
                    try:
                        config = json.loads(content)
                        if 'admins' not in config or 'titles' not in config:
                            raise Exception()
                    except:
                        print(content)
                        Logger.log_error('Malformed cache, starting with a fresh cache')
                        config = {'admins' : {}, 'titles': {}}

                    cls.chat_admins = config['admins']
                    cls.chat_titles = config['titles']
                else:
                    Logger.log_info('Config file appears to be empty')
                    cls.chat_admins = {}
                    cls.chat_titles = {}
        else:
            Logger.log_error('Config file does not exist (This error can be ignored on the initial run)')
            cls.chat_admins = {}
            cls.chat_titles = {}

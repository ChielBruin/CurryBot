import os, json

from data import Logger
from handlers.messageHandler import MessageHandler


class Config (object):
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
    def store_config(cls, bot):
        Logger.log_debug('Serializing config')
        handlers = {}
        for chat_id in bot._chat_message_handlers:
            handlers[chat_id] = {}
            chat_handlers = bot._chat_message_handlers[chat_id]
            for (name, handler) in chat_handlers:
                handlers[chat_id][name] = handler.to_dict()

        tick_handlers = {}
        for (name, handler) in bot._tick_handlers:
            tick_handlers[name] = handler.to_dict()

        config = {
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

                handlers = config['handlers'] if 'handlers' in config else {}
                for chat_id in handlers:
                    chat_handlers = handlers[chat_id]
                    for handler_name in chat_handlers:
                        handler_dict = chat_handlers[handler_name]
                        handler = MessageHandler.class_from_dict(handler_dict).from_dict(handler_dict)
                        bot.register_message_handler(chat_id, handler, handler_name)

                handlers = config['tick_handlers'] if 'tick_handlers' in config else {}
                for chat_id in handlers:
                    chat_handlers = handlers[chat_id]
                    for handler_name in chat_handlers:
                        handler_dict = chat_handlers[handler_name]
                        handler = MessageHandler.class_from_dict(handler_dict).from_dict(handler_dict)
                        bot.register_tick_handler(chat_id, handler, handler_name)

        else:
            Logger.log_error('Config file does not exist (This error can be ignored on the initial run)')

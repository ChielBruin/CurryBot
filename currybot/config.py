import json
import os

from currybot.data import Logger


class Config(object):
    config_location = None

    @classmethod
    def set_config_location(cls, loc):
        Logger.log_trace('Config location set to \'%s\'' % loc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        if os.path.isfile(loc):
            Logger.log_error('The specified config location must be a folder, \'%s\' is a file' % loc)
            raise Exception()
        cls.config_location = os.path.join(loc, 'bot_config.json')

    @classmethod
    def store_config(cls, bot):
        Logger.log_debug('Serializing config')
        message_handlers, global_message_handlers = bot.message_handlers.to_dict()
        button_handlers,  global_button_handlers  = bot.button_handlers.to_dict()
        tick_handlers,    global_tick_handlers    = bot.tick_handlers.to_dict()

        config = {
            'handlers': message_handlers,
            'handlers_global': global_message_handlers,
            'tick_handlers': tick_handlers,
            'tick_handlers_global': global_tick_handlers,
            'button_handlers': button_handlers,
            'button_handlers_global': global_button_handlers
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
                except json.JSONDecodeError:
                    config = {}
                    Logger.log_error('Malformed config file')

                message_handlers        = config['handlers']               if 'handlers'               in config else {}
                global_message_handlers = config['handlers_global']        if 'handlers_global'        in config else {}
                button_handlers         = config['button_handlers']        if 'button_handlers'        in config else {}
                global_button_handlers  = config['button_handlers_global'] if 'button_handlers_global' in config else {}
                tick_handlers           = config['tick_handlers']          if 'tick_handlers'          in config else {}
                global_tick_handlers    = config['tick_handlers_global']   if 'tick_handlers_global'   in config else {}

                bot.message_handlers.from_dict(message_handlers, global_message_handlers)
                bot.button_handlers.from_dict(button_handlers, global_button_handlers)
                bot.tick_handlers.from_dict(tick_handlers, global_tick_handlers)

        else:
            Logger.log_error('Config file does not exist (This error can be ignored on the initial run)')
        bot.init_global_handlers()

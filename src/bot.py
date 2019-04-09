from telegram.ext import Updater, MessageHandler, Filters

from messageHandler import CurryBotMessageHandler

class CurryBot (object):
    def __init__(self, token):
        '''
        Initialize CurryBot
        '''
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(MessageHandler(Filters.text,
                                    (lambda bot, update, self=self: self.on_receive_message(bot, update))))
        self.handlers = {}
        self.keys = {}

    def on_receive_message(self, bot, update):
        '''
        Global message handler.
        Forwards the messages to the other handlers if applicable.
        '''
        for action in self.handlers:
            handler = self.handlers[action]
            if handler.regex:
                handler.on_receive_message(bot, update)

    def start(self):
        '''
        Start the bot.
        '''
        self.updater.start_polling()
        print('CurryBot started')
        self.updater.idle()

    def config_action(self, action_name, action_config):
        '''
        Configure the given action handler withe the given configuration.
        If the handler already exists, update it.
        '''
        if action_name not in self.handlers:
            self.handlers[action_name] = CurryBotMessageHandler(self, action_config)
        else:
            self.handlers[action_name].update(action_config)

    def add_api_key(self, name, key):
        '''
        Add a key to the keystore.
        '''
        self.keys[name] = key

    def get_api_key(self, name):
        '''
        Get a key from the keystore.
        '''
        return self.keys[name]

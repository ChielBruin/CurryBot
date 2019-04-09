from telegram.ext import Updater, MessageHandler, Filters

from messageHandler import CurryBotMessageHandler

class CurryBot (object):
    def __init__(self, token):
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(MessageHandler(Filters.text,
                                    (lambda bot, update, self=self: self.on_receive_message(bot, update))))
        self.handlers = {}
        self.keys = {}

    def on_receive_message(self, bot, update):
        for action in self.handlers:
            handler = self.handlers[action]
            if handler.regex:
                handler.on_receive_message(bot, update)

    def start(self):
        self.updater.start_polling()
        print('CurryBot started')
        self.updater.idle()

    def config_action(self, action_name, action_config):
        if action_name not in self.handlers:
            self.handlers[action_name] = CurryBotMessageHandler(self, action_config)
        else:
            self.handlers[action_name].update(action_config)

    def add_api_key(self, name, key):
        self.keys[name] = key

    def get_api_key(self, name):
        return self.keys[name]

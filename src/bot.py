from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

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
        self.dispatcher.add_handler(CommandHandler('info',
                                       (lambda bot, update, self=self: self.on_info_command(bot, update))))

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

    def on_info_command(self, bot, update):
        '''
        Triggers when the /info command is used.
        Prints relevant chat info to the console.
        If replied to a sticker, print the sticker id as well.
        '''
        try:
            message = update.message
            bot.forward_message(message.chat.id, from_chat_id=310311697, message_id=1515)

            print('\nInfo command used:')
            print('\tChat_id: %d' % message.chat.id)
            if message.reply_to_message:
                message = message.reply_to_message
                if message.sticker:
                    sticker = message.sticker
                    print('\tSticker')
                    print('\t  Sticker_id: %s' % sticker.file_id)
                    print('\t  Pack_id: %s' % sticker.set_name)
                elif message.forward_from:
                    print('\tForwarded message')
                    print('\t  Message_id: %d' % message.message_id)

                else:
                    print(message)
            else:
                msg = '`putStrLn "Hello, World!"`\nI reply to your messages when I feel the need to.'
                bot.send_message(chat_id=message.chat_id, text=msg, parse_mode='Markdown')
            print()
        except Exception as e:
            print('Error in info command handling:')
            print(e)
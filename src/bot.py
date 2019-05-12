from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

from datetime import datetime, timedelta

from messageHandler import CurryBotMessageHandler

class CurryBot (object):
    def __init__(self, token):
        '''
        Initialize CurryBot
        '''
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.active_timers = {}

        self.dispatcher.add_handler(MessageHandler(Filters.text,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'text'))))
        self.dispatcher.add_handler(MessageHandler(Filters.audio,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'audio'))))
        self.dispatcher.add_handler(MessageHandler(Filters.contact,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'contact'))))
        self.dispatcher.add_handler(MessageHandler(Filters.document,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'document'))))
        self.dispatcher.add_handler(MessageHandler(Filters.photo,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'image'))))
        self.dispatcher.add_handler(MessageHandler(Filters.sticker,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'sticker'))))
        self.dispatcher.add_handler(MessageHandler(Filters.video,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'video'))))
        self.dispatcher.add_handler(MessageHandler(Filters.voice,
                                    (lambda bot, update, self=self: self.on_receive(bot, update, 'voice'))))
        self.dispatcher.add_handler(CommandHandler('info',
                                    (lambda bot, update, self=self: self.on_info_command(bot, update))))

        self.handlers = {}
        self.keys = {}

    def on_receive(self, bot, update, message_type):
        '''
        Global message handler.
        Forwards the messages to the other handlers if applicable.
        '''
        try:
            if not message_type == 'tick':
                chat_id = str(update.message.chat.id)
                self.active_timers[chat_id] = datetime.now()

            for action in self.handlers:
                handler = self.handlers[action]
                if message_type in handler.triggers:
                    actionHandlers = handler.triggers[message_type]
                    for actionHandler in actionHandlers:
                        actionHandler(bot, update)
        except Exception as e:
            print('Error in \'on_receive_message\':')
            print(e)

    def tick(self, bot, job):
        '''
        Propagate the tick action to all the registered handlers.
        '''
        now = datetime.now()
        deltas = {}
        for chat_id in self.active_timers:
            chat_id = str(chat_id)
            deltas[chat_id] = now - self.active_timers[chat_id]
        self.on_receive(bot, deltas, 'tick')

    def start(self):
        '''
        Start the bot.
        '''
        self.updater.start_polling()
        print('CurryBot started')

        # Set up the tick trigger
        self.dispatcher.job_queue.run_repeating(self.tick,
                timedelta(minutes=1), first=timedelta(seconds= 60 - datetime.now().second))

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

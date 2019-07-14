from telegram.ext import Updater, CommandHandler, Filters
from telegram.ext import MessageHandler as TelegramMessageHandler

from datetime import datetime, timedelta

from logger import Logger
from cache import Cache


class CurryBot (object):
    def __init__(self):
        '''
        Initialize CurryBot
        '''
        self.bot = None
        self.updater = None
        self.dispatcher = None

        self._message_handlers = []
        self._tick_handlers = []

    def set_token(self, token):
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

        self.dispatcher.add_handler(TelegramMessageHandler(Filters.all,
                                    (lambda bot, update, self=self: self.on_receive(bot, update))))
        self.dispatcher.add_handler(CommandHandler('info',
                                    (lambda bot, update, self=self: self.on_info_command(bot, update))))
        self.dispatcher.add_handler(CommandHandler('update',
                                    (lambda bot, update, self=self: self.on_update_command(bot, update))))

    def register_message_handler(self, handler):
        self._message_handlers.append(handler)

    def register_tick_handler(self, handler):
        self._tick_handlers.append(handler)

    def on_receive(self, bot, update):
        self.on_receive_message(bot, update.message)

    def on_receive_message(self, bot, message):
        '''
        Global message handler.
        Forwards the messages to the other handlers if applicable.
        '''
        try:
            for handler in self._message_handlers:
                    handler.call(bot, message)
        except Exception as ex:
            Logger.log_exception(msg='This exception should never occur')

    def on_receive_tick(self, bot, job):
        try:
            time = datetime.now()
            for handler in self._tick_handlers:
                    handler.call(bot, time)
        except Exception as ex:
            Logger.log_exception(ex, msg='This exception should never occur')

    def update_cache(self):
        Logger.log_info('Updating cache')
        for handler in self._message_handlers:
            handler.update()
        for handler in self._tick_handlers:
            handler.update()
        Cache.store_cache()

    def start(self):
        '''
        Start the bot.
        '''
        self.updater.start_polling()

        # Set up the tick trigger
        self.dispatcher.job_queue.run_repeating(self.on_receive_tick,
                timedelta(minutes=1), first=timedelta(seconds= 60 - datetime.now().second))
        self.dispatcher.job_queue.run_repeating(lambda b, j, self=self: self.update_cache(),
                timedelta(days=1), first=timedelta(hours= 24 - datetime.now().hour))

        Logger.log_info('CurryBot started')
        self.updater.idle()

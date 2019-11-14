from telegram.ext import Updater, Filters, CallbackQueryHandler
from telegram.ext import MessageHandler as TelegramMessageHandler
import traceback

from datetime import datetime, timedelta

from logger import Logger
from cache import Cache
from config import Config
from configConversation import ConfigConversation
from exceptions import FilterException

class CurryBot (object):
    def __init__(self):
        '''
        Initialize CurryBot
        '''
        self.bot = None
        self.updater = None
        self.dispatcher = None

        self._global_message_handlers = []
        self._chat_message_handlers = {}
        self._tick_handlers = []
        self.chat_admins = {}

    def set_token(self, token):
        self.updater = Updater(token, user_sig_handler=lambda s, f, self=self: self.on_exit())
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

        self.dispatcher.add_handler(ConfigConversation(self).get_conversation_handler())
        self.dispatcher.add_handler(TelegramMessageHandler(Filters.all,
                            (lambda bot, update, self=self: self.on_receive(bot, update))))

    def register_message_handler(self, chat=None, handler=None, name=None):
        if not handler:
            raise Exception('No handler provided when registering a handler')
        if not name:
            raise Exception('No name provided when registering a handler')
        if chat is None:
            self._global_message_handlers.append((name, handler))
        else:
            if chat in self._chat_message_handlers:
                self._chat_message_handlers[chat].append((name, handler))
            else:
                self._chat_message_handlers[chat] = [(name, handler)]

    def register_tick_handler(self, handler, name):
        self._tick_handlers.append((name, handler))

    def on_receive(self, bot, update):
        chat = update.message.chat
        if chat.title:  # If not private chat
            Config.set_chat_title(chat.id, chat.title)

        if update.message:
            message = update.message
        elif update.edited_message:
            message = update.edited_message
        else:
            return
        self.on_receive_message(bot, message)

    def on_receive_message(self, bot, message):
        '''
        Global message handler.
        Forwards the messages to the other handlers if applicable.
        '''
        def call_handler(handler, bot, message):
            try:
                res = handler.call(bot, message, None, [])
                if res is None:
                    Logger.log_error(msg='Handler returned None instead of [..]')
            except FilterException:
                pass
            except Exception as ex:
                Logger.log_exception(ex, msg='Exception while handling message')
                traceback.print_exc()

        for (_, handler) in self._global_message_handlers:
            call_handler(handler, bot, message)

        chat_id = message.chat.id
        if chat_id in self._chat_message_handlers:
            for (_, handler) in self._chat_message_handlers[chat_id]:
                call_handler(handler, bot, message)

    def on_receive_tick(self, bot, job):
        try:
            time = datetime.now()
            for (_, handler) in self._tick_handlers:
                handler.call(bot, time)
        except Exception as ex:
            Logger.log_exception(ex, msg='This exception should never occur')

    def update_cache(self):
        Logger.log_debug('Updating cache')
        for (_, handler) in self._global_message_handlers:
            handler.update()
        for chat in self._chat_message_handlers:
            for (_, handler) in self._chat_message_handlers[chat]:
                handler.update()
        for (_, handler) in self._tick_handlers:
            handler.update()
        Cache.store_cache()
        Config.store_config()

    def on_exit(self):
        Logger.log_info(msg='Shutting down')
        Cache.store_cache()
        Config.store_config()

    def has_handler_with_name(self, new_name):
        for (name, _) in self._global_message_handlers:
            if name == new_name:
                return True
        for chat in self._chat_message_handlers:
            for (name, _) in self._chat_message_handlers[chat]:
                if name == new_name:
                    return True
        return False

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

        Logger.log_info('%s started' % self.bot.first_name)
        self.updater.idle()

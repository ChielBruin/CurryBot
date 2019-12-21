from telegram.ext import Updater, Filters, CallbackQueryHandler
from telegram.ext import MessageHandler as TelegramMessageHandler
from telegram import Chat, Message
import traceback

from datetime import datetime, timedelta

from data import Logger, Cache
from config import Config
from configConversation import ConfigConversation
from exceptions import FilterException

from handlers.messageHandler import MessageHandler
from handlers import MakeSenderBotAdmin, IsCommand, SendTextMessage, IsReply, SwapReply, SenderIsBotAdmin


class SelfJoinedChat (MessageHandler):
    '''
    It makes no sense that users add this filter to their configs, as it can only be added after the bot has already joined.
    '''
    def __init__(self, children):
        super(SelfJoinedChat, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.new_chat_members:
            try:
                next(filter(lambda usr: usr.id == bot.id, message.new_chat_members))
                message.text = bot.first_name
                return self.propagate(bot, message, target, exclude)
            except StopIteration as e:
                raise FilterException()
        else:
            raise FilterException()

class CurryBot (object):
    def __init__(self):
        '''
        Initialize CurryBot
        '''
        self.bot = None
        self.updater = None
        self.dispatcher = None

        self._chat_message_handlers = {}
        self._tick_handlers = {}
        self._button_handlers = {}
        self._global_handlers = None

    def set_token(self, token):
        self.updater = Updater(token, user_sig_handler=lambda s, f, self=self: self.on_exit())
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

        self.dispatcher.add_handler(ConfigConversation(self).get_conversation_handler())
        self.dispatcher.add_handler(CallbackQueryHandler(
                            (lambda bot, update, self=self: self.on_receive_callback(bot, update))))
        self.dispatcher.add_handler(TelegramMessageHandler(Filters.all,
                            (lambda bot, update, self=self: self.on_receive(bot, update))))

    def init_logger(self, admin_chat):
        config = {}
        if admin_chat:
            config[str(admin_chat)] = 2
        Logger.init(self.bot, config)

    def init_global_handlers(self):
        self._global_handlers = [
            SelfJoinedChat([MakeSenderBotAdmin(), SendTextMessage(['Hello everyone! Configure me by sending /config in private chat'], False, None)]),
            IsCommand('/make_?[Aa]dmin', SenderIsBotAdmin([IsReply([SwapReply([MakeSenderBotAdmin(), SendTextMessage(['%h is now admin'], False, None)])])]))
        ]

    def list_tick_handlers(self, chat_id):
        if chat_id in self._tick_handlers:
            return self._tick_handlers[chat_id]
        else:
            return []

    def list_message_handlers(self, chat_id):
        if chat_id in self._chat_message_handlers:
            return self._chat_message_handlers[chat_id]
        else:
            return []

    def list_button_handlers(self, chat_id):
        if chat_id in self._button_handlers:
            return self._button_handlers[chat_id]
        else:
            return []

    def register_button_handler(self, chat, handler, name):
        self._register_handler(self._button_handlers, chat, handler, name)

    def remove_button_handler(self, chat, name):
        self._remove_handler(self._button_handlers, chat, name)

    def register_message_handler(self, chat, handler, name):
        self._register_handler(self._chat_message_handlers, chat, handler, name)

    def remove_message_handler(self, chat, name):
        self._remove_handler(self._chat_message_handlers, chat, name)

    def register_tick_handler(self, chat, handler, name):
        self._register_handler(self._tick_handlers, chat, handler, name)

    def remove_tick_handler(self, chat, name):
        self._remove_handler(self._tick_handlers, chat, name)

    def _remove_handler(self, dict, chat, handler_name):
        chat = str(chat)
        if chat in dict:
            dict[chat] = [(name, handler) for (name, handler) in dict[chat] if not name == handler_name]

    def _register_handler(self, dict, chat, handler, name):
        chat = str(chat)
        if chat in dict:
            dict[chat].append((name, handler))
        else:
            dict[chat] = [(name, handler)]
        handler.update(self.bot)

    def on_receive(self, bot, update):
        if update.message:
            message = update.message
        elif update.edited_message:
            message = update.edited_message
        else:
            return

        chat = update.message.chat
        if chat.title:  # If not private chat
            Cache.set_chat_title(chat.id, chat.title)

        if message.caption:
            message.text = message.caption

        self.on_receive_message(bot, message)

    def call_handler(self, handler, bot, message):
        if message.text is None:
            message.text = ''
        try:
            res = handler.call(bot, message, None, [])
            if res is None:
                Logger.log_error(msg='Handler returned None instead of [..]')
        except FilterException:
            pass
        except Exception as ex:
            Logger.log_exception(ex, msg='Exception while handling message', chat=message.chat.id)
            traceback.print_exc()

    def on_receive_message(self, bot, message):
        '''
        Global message handler.
        Forwards the messages to the other handlers if applicable.
        Always calls the handler that checks if the bot was added to a group.
        '''
        for handler in self._global_handlers:
            self.call_handler(handler, bot, message)

        chat_id = str(message.chat.id)
        if chat_id in self._chat_message_handlers:
            for (_, handler) in self._chat_message_handlers[chat_id]:
                self.call_handler(handler, bot, message)

    def on_receive_callback(self, bot, update):
        query = update.callback_query
        if query.message.reply_to_message:
            reply_to = query.message.reply_to_message
            text = '%s_%s' % (query.data, query.message.reply_to_message.text)
        else:
            reply_to = None
            text = query.data

        message = Message(-1, query.from_user, query.message.date, query.message.chat, text=text, reply_to_message=reply_to)
        chat_id = str(query.message.chat.id)
        if chat_id in self._button_handlers:
            for (_, handler) in self._button_handlers[chat_id]:
                self.call_handler(handler, bot, message)

    def on_receive_tick(self, bot, job):
        time = datetime.now()
        for chat_id in self._tick_handlers:
            chat = Chat(chat_id, 'tick_group %s' % chat_id)
            message = Message(-1, None, time, chat, text='tick @ %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
            for (_, handler) in self._tick_handlers[chat_id]:
                self.call_handler(handler, bot, message)

    def update_cache(self):
        Logger.log_debug('Updating cache')
        for chat in self._chat_message_handlers:
            for (_, handler) in self._chat_message_handlers[chat]:
                handler.update(self.bot)
        for chat in self._tick_handlers:
            for (_, handler) in self._tick_handlers[chat]:
                handler.update(self.bot)
        for chat in self._button_handlers:
            for (_, handler) in self._button_handlers[chat]:
                handler.update(self.bot)
        Cache.store_cache()
        Config.store_config()

    def on_exit(self):
        Logger.log_info(msg='Shutting down')
        Cache.store_cache()
        Config.store_config(self)

    def has_handler_with_name(self, new_name):
        for chat in self._chat_message_handlers:
            for (name, _) in self._chat_message_handlers[chat]:
                if name == new_name:
                    return True
        for chat in self._tick_handlers:
            for (name, _) in self._tick_handlers[chat]:
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

        Cache.store_cache()
        Config.store_config(self)

        self.updater.idle()

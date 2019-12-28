from telegram.ext import Updater, Filters, CallbackQueryHandler
from telegram.ext import MessageHandler as TelegramMessageHandler
from telegram import Chat, Message
import traceback

from datetime import datetime, timedelta

from data import Logger, Cache
from config import Config
from configConversation import ConfigConversation
from exceptions import FilterException
from handlerGroup import HandlerGroup

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
    def __init__(self, admin_chat):
        '''
        Initialize CurryBot
        '''
        self.admin_chat = admin_chat
        self.bot = None
        self.updater = None
        self.dispatcher = None

        self._global_message_handlers = {}
        self.message_handlers = None
        self.tick_handlers    = None
        self.button_handlers  = None

    def set_token(self, token):
        self.updater = Updater(token, user_sig_handler=lambda s, f, self=self: self.on_exit())
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

        self.message_handlers = HandlerGroup(self.bot)
        self.tick_handlers    = HandlerGroup(self.bot)
        self.button_handlers  = HandlerGroup(self.bot)

        self.dispatcher.add_error_handler(self.on_error)
        self.dispatcher.add_handler(ConfigConversation(self).get_conversation_handler())
        self.dispatcher.add_handler(CallbackQueryHandler(
                            (lambda bot, update, self=self: self.on_receive_callback(bot, update))))
        self.dispatcher.add_handler(TelegramMessageHandler(Filters.all,
                            (lambda bot, update, self=self: self.on_receive(bot, update))))

    def init_logger(self):
        config = {}
        if self.admin_chat:
            config[str(self.admin_chat)] = 2
        Logger.init(self.bot, config)

    def init_global_handlers(self):
        self._global_handlers = [
            SelfJoinedChat([MakeSenderBotAdmin(), SendTextMessage(['Hello everyone! Configure me by sending /config in private chat'], False, None)]),
            IsCommand('/make_?[Aa]dmin', SenderIsBotAdmin([IsReply([SwapReply([MakeSenderBotAdmin(), SendTextMessage(['%h is now admin'], False, None)])])]))
        ]

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

    def on_receive_message(self, bot, message):
        '''
        Global message handler.
        Forwards the messages to the other handlers if applicable.
        Always calls the handler that checks if the bot was added to a group.
        '''
        try:
            for handler in self._global_handlers:
                self.message_handlers._call_handler(handler, bot, message)
            self.message_handlers.call(bot, message)
        except:
            Logger.log_error('Exception while handling message')
            traceback.print_exc()

    def on_receive_callback(self, bot, update):
        try:
            query = update.callback_query
            if query.message.reply_to_message:
                reply_to = query.message.reply_to_message
                text = '%s_%s' % (query.data, query.message.reply_to_message.text)
            else:
                reply_to = None
                text = query.data

            message = Message(-1, query.from_user, query.message.date, query.message.chat, text=text, reply_to_message=reply_to)
            self.button_handlers.call(bot, message)
        except:
            Logger.log_error('Exception while handling button event')
            traceback.print_exc()

    def on_receive_tick(self, bot, job):
        try:
            time = datetime.now()
            text = time.strftime('%Y-%m-%d %H:%M:%S')
            messages = [Message(-1, None, time, Chat(chat_id, 'tick_group %s' % chat_id), text=text) for chat_id in Cache.list_chat_ids()]
            self.tick_handlers.call(bot, messages)
        except:
            Logger.log_error('Exception while handling tick')
            traceback.print_exc()

    def update_cache(self):
        Logger.log_debug('Updating cache')

        self.message_handlers.update()
        self.button_handlers.update()
        self.tick_handlers.update()

        Cache.store_cache()
        Config.store_config()

    def on_exit(self):
        Logger.log_info(msg='Shutting down')
        Cache.store_cache()
        Config.store_config(self)

    def has_handler_with_name(self, chat_id, new_name):
        return (
            self.message_handlers.contains(chat_id, new_name) or
            self.button_handlers.contains(chat_id, new_name) or
            self.tick_handlers.contains(chat_id, new_name)
        )

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

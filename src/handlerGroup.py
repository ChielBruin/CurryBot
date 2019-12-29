import traceback

from handlers.messageHandler import MessageHandler
from exceptions import FilterException
from data import Logger


class HandlerGroup (object):
    GLOBAL = 'GLOBAL'

    def __init__(self, bot):
        self._handlers = {}
        self._global_handlers = []
        self._bot = bot

    def list(self, chat_id):
        chat_id = str(chat_id)
        if chat_id == self.GLOBAL:
            return self._global_handlers
        if chat_id in self._handlers:
            return self._handlers[chat_id]
        else:
            return []

    def remove(self, chat, handler_name):
        chat = str(chat)
        if chat == self.GLOBAL:
            self._global_handlers = [(name, handler) for (name, handler) in self._global_handlers if not name == handler_name]
        if chat in self._handlers:
            self._handlers[chat] = [(name, handler) for (name, handler) in self._handlers[chat] if not name == handler_name]

    def register(self, chat, handler, name):
        chat = str(chat)
        if chat == self.GLOBAL:
            self._global_handlers.append( (name, handler) )
        elif chat in self._handlers:
            self._handlers[chat].append((name, handler))
        else:
            self._handlers[chat] = [(name, handler)]
        handler.update(self._bot)

    def update(self):
        for (_, handler) in self._global_handlers[chat]:
            handler.update(self._bot)

        for chat in self._handlers:
            for (_, handler) in self._handlers[chat]:
                handler.update(self._bot)

    def contains(self, chat_id, new_name):
        for (name, _) in self._global_handlers:
            if name == new_name:
                return True

        if chat_id in self._handlers:
            for (name, _) in self._handlers[chat_id]:
                if name == new_name:
                    return True
        return False

    def to_dict(self):
        dict = {}
        for chat_id in self._handlers:
            dict[chat_id] = {}
            for (name, handler) in self._handlers[chat_id]:
                dict[chat_id][name] = handler.to_dict()

        global_dict = {}
        for (name, handler) in self._global_handlers:
            global_dict[name] = handler.to_dict()
        return dict, global_dict

    def handler_to_dict(self, chat_id, handler_name):
        if chat_id in self._handlers:
            for (name, handler) in self._handlers[chat_id]:
                if name == handler_name:
                    return handler.to_dict()
        return {}

    def update_handler_from_dict(self, chat_id, handler_name, dict):
        new_handler = MessageHandler.class_from_dict(dict).from_dict(dict)
        new_handler.update(self._bot)

        if chat_id in self._handlers:
            self._handlers[chat_id] = [(name, new_handler if name == handler_name else handler) for (name, handler) in self._handlers[chat_id]]


    def from_dict(self, dict, global_dict):
        for chat_id in dict:
            chat_handlers = dict[chat_id]
            for handler_name in chat_handlers:
                handler_dict = chat_handlers[handler_name]
                handler = MessageHandler.class_from_dict(handler_dict).from_dict(handler_dict)
                self.register(chat_id, handler, handler_name)

        for handler_name in global_dict:
            handler_dict = global_dict[handler_name]
            handler = MessageHandler.class_from_dict(handler_dict).from_dict(handler_dict)
            self.register(self.GLOBAL, handler, handler_name)

    def _call_handler(self, handler, bot, message):
        try:
            res = handler.call(bot, message, None, [])
            if res is None:
                Logger.log_error(msg='Handler %s returned None instead of [..]' % type(handler).__name__)
        except FilterException:
            pass
        except Exception as ex:
            Logger.log_exception(ex, msg='Exception while handling message', chat=message.chat.id)
            traceback.print_exc()

    def call(self, bot, messages):
        if not isinstance(messages, list):
            messages = [messages]

        for message in messages:
            chat_id = str(message.chat.id)
            for (_, handler) in self._global_handlers:
                self._call_handler(handler, bot, message)

            chat_id = str(message.chat.id)
            if chat_id in self._handlers:
                for (_, handler) in self._handlers[chat_id]:
                    self._call_handler(handler, bot, message)

    def migrate(self, from_id, to_id):
        if from_id in self._handlers:
            self._handlers[to_id] = self._handlers[from_id]
            self._handlers.pop(from_id, None)

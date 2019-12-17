import re

from ..messageHandler import MessageHandler
from exceptions       import FilterException
from data             import Config
from configResponse   import Send, Done, AskChild, NoChild, CreateException


class SenderIsBotAdmin (MessageHandler):
    def __init__(self, children):
        super(SenderIsBotAdmin, self).__init__(children)

    def call(self, bot, message, target, exclude):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if Config.is_chat_admin(chat_id, user_id):
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Sender is bot admin"

    @classmethod
    def _from_dict(cls, dict, children):
        return SenderIsBotAdmin(children)

    def _to_dict(self):
        return {}

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(SenderIsBotAdmin(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for SenderIsBotAdmin')

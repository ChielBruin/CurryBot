from ..messageHandler import MessageHandler
from data import Cache


class MakeSenderBotAdmin (MessageHandler):
    def __init__(self):
        super(MakeSenderBotAdmin, self).__init__([])

    def call(self, bot, msg, target, exclude):
        Cache.add_chat_admin(msg.chat.id, msg.from_user.id)
        return []

    def has_effect():
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Make sender bot admin"

    @classmethod
    def create(cls, stage, data, arg):
        return (-1, None, Done(MakeSenderBotAdmin()))

    @classmethod
    def _from_dict(cls, dict, children):
        return MakeSenderBotAdmin()

    def _to_dict(self):
        return {}

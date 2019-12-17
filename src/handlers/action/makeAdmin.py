from ..messageHandler import MessageHandler
from data import Cache, Logger


class MakeSenderBotAdmin (MessageHandler):
    def __init__(self):
        super(MakeSenderBotAdmin, self).__init__([])

    def call(self, bot, msg, target, exclude):
        Logger.log_info('Added %s as bot admin' % msg.from_user.first_name)
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

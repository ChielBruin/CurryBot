from currybot.configResponse import Done
from currybot.handlers.messageHandler import MessageHandler
from currybot.data import Cache, Logger


class MakeSenderBotAdmin(MessageHandler):
    def __init__(self):
        super(MakeSenderBotAdmin, self).__init__([])

    def call(self, bot, message, target, exclude):
        Logger.log_info('Added %s as bot admin' % message.from_user.first_name)
        Cache.add_chat_admin(message.chat.id, message.from_user.id)
        return []

    def has_effect(self):
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

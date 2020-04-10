from currybot.configResponse import Send, Done, AskChild, CreateException
from currybot.handlers.messageHandler import MessageHandler


class Delete(MessageHandler):
    def __init__(self):
        super(Delete, self).__init__([])

    def call(self, bot, msg, target, exclude):
        bot.delete_message(msg.chat.id, msg.message_id)
        return []

    @classmethod
    def is_entrypoint(cls):
        return False

    def has_effect(self):
        return True

    @classmethod
    def get_name(cls):
        return "Delete the message"

    def _to_dict(self):
        return {}

    @classmethod
    def _from_dict(cls, dict, children):
        return Delete()

    @classmethod
    def create(cls, stage, data, arg):
        return (-1, None, Done(Delete()))

from currybot.configResponse import Send, Done, AskChild, CreateException
from currybot.handlers.messageHandler import MessageHandler


class SetTitle(MessageHandler):
    def __init__(self):
        super(SetTitle, self).__init__([])

    def call(self, bot, msg, target, exclude):
        bot.set_chat_title(msg.chat.id, msg.text)
        return []

    @classmethod
    def is_entrypoint(cls):
        return False

    def has_effect(self):
        return True

    @classmethod
    def get_name(cls):
        return "Set the chat title"

    def _to_dict(self):
        return {}

    @classmethod
    def _from_dict(cls, dict, children):
        return SetTitle()

    @classmethod
    def create(cls, stage, data, arg):
        return (-1, None, Done(SetTitle()))

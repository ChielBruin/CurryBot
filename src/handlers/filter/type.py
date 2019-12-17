import re
from telegram import MessageEntity

from ..messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, NoChild, CreateException

class AbstractIsType (MessageHandler):
    def __init__(self, children):
        super(AbstractIsType, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if self.check(message):
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(cls._from_dict({}, data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for abstractIsType')

    def _to_dict(self):
        return {}


class IsReply (AbstractIsType):
    def __init__(self, children):
        super(IsReply, self).__init__(children)

    def check(self, message):
        if message.reply_to_message:
            return True
        else:
            return False

    @classmethod
    def get_name(cls):
        return "Message is reply"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsReply(children)


class IsForward (AbstractIsType):
    def __init__(self, children):
        super(IsForward, self).__init__(children)

    def check(self, message):
        if message.forward_from:
            return True
        else:
            return False

    @classmethod
    def get_name(cls):
        return "Message is forwarded"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsReply(children)

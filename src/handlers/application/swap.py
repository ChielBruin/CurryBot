from ..messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, NoChild, CreateException


class SwapReply (MessageHandler):
    def __init__(self, children):
        super(SwapReply, self).__init__(children)


    def call(self, bot, msg, target, exclude):
        if msg.reply_to_message:
            msg.reply_to_message.reply_to_message = msg
            return self.propagate(bot, msg.reply_to_message, target, exclude)
        else:
            Logger.log_error('Message is not a reply')
            return []

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Swap reply messages"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(SwapReply(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for swapReply')

    @classmethod
    def _from_dict(cls, dict, children):
        return SwapReply(children)

    def _to_dict(self):
        return {}

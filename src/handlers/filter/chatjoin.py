from telegram import MessageEntity

from messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, NoChild, CreateException


class UserJoinedChat (MessageHandler):
    def __init__(self, children):
        super(UserJoinedChat, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.new_chat_members:
            res = []
            for member in message.new_chat_members:
                message.from_user = member
                res.extend(self.propagate(bot, message, target, exclude))
            return res
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Someone joined the chat"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(UserJoinedChat(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for userJoinedChat')

    @classmethod
    def _from_dict(cls, dict, children):
        return UserJoinedChat(children)

    def _to_dict(self):
        return {}

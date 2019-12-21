from ..messageHandler import MessageHandler
from exceptions import FilterException
from configResponse import Send, Done, AskChild, NoChild, CreateException

import copy


class Try (MessageHandler):
    def __init__(self, children):
        super(Try, self).__init__(children)

    def call(self, bot, message, target, exclude):
        for child in self.children:
            try:
                return child.call(bot, message, target, copy.copy(exclude))
            except FilterException:
                continue
        raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Try child, if fails continue to next"

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], AskChild())
        elif stage == 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage == 1 and isinstance(arg, NoChild):
            return (-1, None, Done(Try(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for try')

    @classmethod
    def _from_dict(cls, dict, children):
        return Try(children)

    def _to_dict(self):
        return {}

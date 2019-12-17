from ..messageHandler import MessageHandler
from exceptions import FilterException
from configResponse import Send, Done, AskChild, NoChild, CreateException

import random, copy, re

class PickWeighted (MessageHandler):
    def __init__(self, config):
        self.size = 0
        self.weights = []
        children = []
        for (weight, child) in config:
            children.append(child)
            self.weights.append(weight + self.size)
            self.size += weight
        super(PickWeighted, self).__init__(children)

    def call(self, bot, msg, target, exclude):
        rand = random.randrange(self.size)
        for index, weight in enumerate(self.weights):
            if rand <= weight:
                return self.children[index].call(bot, msg, target, exclude)
        print(rand, self.weights)
        raise Exception('Off by at least one in random selection')

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Pick weighted random from children"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append((None, arg))
            return (2, data, Send(msg='Please send a weight'))
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(PickWeighted(data)))
        elif stage is 2 and arg:
            if not arg.text or not re.matches(r'[\d]+$', arg.text):
                return (2, data, Send(msg='Invalid weight, must be a positive integer'))
            else:
                data[-1] = (int(arg.text), arg)
                return (1, data, AskChild())
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for pickWeighted')

    @classmethod
    def _from_dict(cls, dict, children):
        weights = dict['weights']
        return PickWeighted(zip(weights, children))

    def _to_dict(self):
        return {'weights': self.weights}


class PickUniform (MessageHandler):
    def __init__(self, children):
        super(PickUniform, self).__init__(children)

    def call(self, bot, msg, target, exclude):
        index = random.randrange(len(self.children))
        return self.children[index].call(bot, msg, target, exclude)

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Pick uniform random from children"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(PickUniform(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for pickUniform')

    @classmethod
    def _from_dict(cls, dict, children):
        return PickUniform(children)

    def _to_dict(self):
        return {}

from messageHandler import MessageHandler
from exceptions import FilterException

import random, copy

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



class Not (MessageHandler):
    def __init__(self, condition, children):
        super(Not, self).__init__(children)
        if condition.has_effect():
            raise Exception('A handler for Not condition should not have effects')
        self.condition = condition

    def call(self, bot, msg, target, exclude):
        try:
            self.condition.call(bot, copy.copy(msg), target, copy.copy(exclude))
            raise FilterException()
        except FilterException:
            return self.propagate(bot, msg, target, exclude)

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Not"



class PercentageFilter (MessageHandler):
    def __init__(self, percentage, children):
        super(PercentageFilter, self).__init__(children)
        self._percentage = percentage

    def call(self, bot, message, target, exclude):
        if random.randrange(100) <= self._percentage:
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Filter out x% of messages"


class Try (MessageHandler):
    def __init__(self, children, extend=[]):
        super(Try, self).__init__(children)
        for child in self.children:
            child.extend_children(extend)

    def call(self, bot, message, target, exclude):
        for child in self.children:
            try:
                return child.call(bot, message, target, copy.copy(exclude))
            except FilterException:
                continue
        raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Try child, if fails continue to next"



class Swallow (MessageHandler):
    def __init__(self):
        super(Swallow, self).__init__([])

    def call(self, bot, msg, target, exclude):
        return []

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Do nothing"


class Or (Try):
    def __init__(self, filters, children):
        super(Or, self).__init__(filters, extend=children)

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Or"

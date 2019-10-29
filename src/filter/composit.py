from messageHandler import MessageHandler
from exceptions import FilterException

import random, copy

class PickWeighted (MessageHandler):
    def __init__(self, config):
        self.size = 0
        weights = []
        children = []
        for (weight, child) in config:
            children.append(child)
            weights.append(weight + self.size)
            self.size += weight
        super(PickWeighted, self).__init__(children)

    def call(self, bot, msg, target, exclude):
        rand = random.randrange(self.size)
        for index, weight in enumerate(self.weights):
            if rand >= weight:
                return self.children[index].call(bot, msg, target, exclude)
        raise Exception('Off by at least one in random selection')


class PickUniform (MessageHandler):
    def __init__(self, children):
        super(PickUniform, self).__init__(children)

    def call(self, bot, msg, target, exclude):
        index = random.randrange(len(self.children))
        return self.children[index].call(bot, msg, target, exclude)


class PercentageFilter (MessageHandler):
    def __init__(self, percentage, children):
        super(PercentageFilter, self).__init__(children)
        self._percentage = percentage

    def call(self, bot, message, target, exclude):
        if random.randrange(100) <= self._percentage:
            return self.propagate(bot, message, target, exclude)
        else:
            return FilterException()

class Try (MessageHandler):
    def __init__(self, children, extend=[]):
        super(Try, self).__init__(children)
        for child in self.children:
            child.extend_children(extend)

    def call(self, bot, message, target, exclude):
        for child in self.children:
            try:
                return child.call(bot, message, target, copy.copy(exclude))
            except Exception:
                continue
        raise FilterException()


class Swallow (MessageHandler):
    def __init__(self):
        super(Swallow, self).__init__([])

    def call(self, bot, msg, target, exclude):
        return []

class Or (Try):
    def __init__(self, filters, children):
        super(Or, self).__init__(filters, extend=children)

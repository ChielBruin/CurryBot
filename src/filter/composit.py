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


class PickUniform (MessageHandler):
    def __init__(self, children):
        super(PickUniform, self).__init__(children)

    def call(self, bot, msg, target, exclude):
        index = random.randrange(len(self.children))
        return self.children[index].call(bot, msg, target, exclude)


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


class PercentageFilter (MessageHandler):
    def __init__(self, percentage, children):
        super(PercentageFilter, self).__init__(children)
        self._percentage = percentage

    def call(self, bot, message, target, exclude):
        if random.randrange(100) <= self._percentage:
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

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

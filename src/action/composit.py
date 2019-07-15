from action.action import Action

import random


class NoAction (Action):
    def dispatch(self, bot, msg, exclude):
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        return []


class PercentageAction (Action):
    def __init__(self, id, percentage, left, right):
        super(PercentageAction, self).__init__(id)
        self._left = left
        self._right = right
        self._percentage = percentage

    def dispatch(self, bot, msg, exclude):
        if random.randrange(100) <= self._percentage:
            return self._left.dispatch(bot, msg, exclude)
        else:
            return self._right.dispatch(bot, msg, exclude)

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        if random.randrange(100) <= self._percentage:
            return self._left.dispatch_reply(bot, msg, reply_to, exclude)
        else:
            return self._right.dispatch_reply(bot, msg, reply_to, exclude)

class UniformFromAction (Action):
    def __init__(self, id, actions):
        super(UniformFromAction, self).__init__(id)
        self._actions = actions

    def dispatch(self, bot, msg, exclude):
        idx = random.randrange(len(self._actions))
        return self._actions[idx].dispatch(bot, msg, exclude)


    def dispatch_reply(self, bot, msg, reply_to, exclude):
        idx = random.randrange(len(self._actions))
        return self._actions[idx].dispatch_reply(bot, msg, reply_to, exclude)


class AndAction (Action):
    def __init__(self, id, left, right):
        super(AndAction, self).__init__(id)
        self._left = left
        self._right = right

    def update(self):
        self._left.update()
        self._right.update()

    def dispatch(self, bot, msg, exclude):
        r1 = self._left.dispatch(self, bot, msg, exclude)
        r2 = self._right.dispatch(self, bot, msg, exclude)
        r1.extend(r2)
        return r1

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        r1 = self._left.dispatch_reply(self, bot, msg, reply_to, exclude)
        r2 = self._right.dispatch_reply(self, bot, msg, reply_to, exclude)
        r1.extend(r2)
        return r1


class OrAction (Action):
    def __init__(self, id, left, right):
        super(OrAction, self).__init__(id)
        self._left = left
        self._right = right

    def update(self):
        self._left.update()
        self._right.update()

    def dispatch(self, bot, msg, exclude):
        try:
            return self._left.dispatch(self, bot, msg, exclude)
        except:
            return self._right.dispatch(self, bot, msg, exclude)

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        try:
            return self._left.dispatch_reply(self, bot, msg, reply_to, exclude)
        except:
            return self._right.dispatch_reply(self, bot, msg, reply_to, exclude)

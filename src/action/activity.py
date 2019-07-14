from action.action import Action
from cache import Cache
from logger import Logger

import requests

class MonitorUserActivityAction (Action):
    def __init__(self, id):
        super(MonitorUserActivityAction, self).__init__(id)
        self.update()

    def update(self):
        Logger.log('DEBUG', 'Updating cache of %s' % self.id)
        # TODO

    def dispatch(self, bot, msg, exclude):
        # TODO
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        # TODO
        return []


class MonitorChatActivityAction (Action):
    def __init__(self, id):
        super(MonitorChatActivityAction, self).__init__(id)
        self.update()

    def update(self):
        Logger.log('DEBUG', 'Updating cache of %s' % self.id)
        # TODO

    def dispatch(self, bot, msg, exclude):
        # TODO
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        # TODO
        return []

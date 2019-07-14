from action.action import Action
from cache import Cache


class AbstractMonitorActivityAction (Action):
    def __init__(self, id, cache_key):
        super(AbstractMonitorActivityAction, self).__init__(id)
        self.cache_key = cache_key
        self.update()

    def update(self):
        if not Cache.shared_get_cache(self.cache_key):
            Cache.shared_put_cache(self.cache_key, {'chat': {}, 'user': {} })

    def _log_activity(self, message):
        raise Exception('Not implemented')

    def log_activity(self, key, id, time):
        cache = Cache.shared_get_cache(self.cache_key)
        cache[key][id] = time.timestamp()
        Cache.shared_put_cache(self.cache_key, cache)

    def dispatch(self, bot, msg, exclude):
        self._log_activity(msg)
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        self._log_activity(msg)
        return []


class MonitorChatActivityAction (AbstractMonitorActivityAction):
    def _log_activity(self, message):
        self.log_activity('chat', message.chat.id, message.date)


class MonitorUserActivityAction (AbstractMonitorActivityAction):
    def _log_activity(self, message):
        self.log_activity('user', message.from_user.id, message.date)

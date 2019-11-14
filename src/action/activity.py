from messageHandler import MessageHandler
from cache import Cache
from configResponse import Send, Done, AskChild, AskCacheKey, CreateException


class AbstractMonitorActivity (MessageHandler):
    def __init__(self, cache_key):
        super(AbstractMonitorActivity, self).__init__([])
        self.cache_key = cache_key
        self.update()

    def update(self):
        if not Cache.contains(self.cache_key):
            Cache.put(self.cache_key, {'chat': {}, 'user': {} })

    def _log_activity(self, message):
        raise Exception('Not implemented')

    def log_activity(self, key, id, time):
        Cache.put([self.cache_key, key, str(id)], time.timestamp())

    def call(self, bot, msg, target, exclude):
        self._log_activity(msg)
        return []

    def has_effect():
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, AskCacheKey())
        elif stage is 1 and arg:
            return (-1, None, Done(cls._get_instance(arg)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendTextMessage')



class MonitorChatActivity (AbstractMonitorActivity):
    def _log_activity(self, message):
        self.log_activity('chat', message.chat.id, message.date)

    @classmethod
    def _get_instance(cls, key):
        return MonitorChatActivity(key)

    @classmethod
    def get_name(cls):
        return 'Log chat activity'


class MonitorUserActivity (AbstractMonitorActivity):
    def _log_activity(self, message):
        self.log_activity('user', message.from_user.id, message.date)

    @classmethod
    def _get_instance(cls, key):
        return MonitorUserActivity(key)

    @classmethod
    def get_name(cls):
        return 'Log user activity'

from datetime import datetime

from ..messageHandler import MessageHandler
from data import Cache, Logger
from configResponse import Send, Done, AskChild, AskCacheKey, CreateException


class AbstractActivityMonitor (MessageHandler):
    def __init__(self, cache_key):
        super(AbstractActivityMonitor, self).__init__([])
        self.cache_key = cache_key
        self.update()

    def update(self):
        if not Cache.contains(self.cache_key):
            Cache.put(self.cache_key, {'chat': {}, 'user': {} })

    def _log_activity(self, message):
        raise Exception('Not implemented')

    def log_activity(self, key, message):
        id = message.chat.id
        time = datetime.now()
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
            default = {'chat':{}, 'user':{}}
            return (1, None, AskCacheKey(default))
        elif stage is 1 and arg:
            return (-1, None, Done(cls._from_dict({'key': arg}, [])))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for monitor')

    def _to_dict(self):
        return {'key': self.cache_key}



class MonitorChatActivity (AbstractActivityMonitor):
    def _log_activity(self, message):
        self.log_activity('chat', message)

    @classmethod
    def _get_instance(cls, key):
        return MonitorChatActivity(key)

    @classmethod
    def get_name(cls):
        return 'Log chat activity'

    @classmethod
    def _from_dict(cls, dict, children):
        return MonitorChatActivity(dict['key'])


class MonitorUserActivity (AbstractActivityMonitor):
    def _log_activity(self, message):
        self.log_activity('user', message)

    @classmethod
    def _get_instance(cls, key):
        return MonitorUserActivity(key)

    @classmethod
    def _from_dict(cls, dict, children):
        return MonitorUserActivity(dict['key'])

    @classmethod
    def get_name(cls):
        return 'Log user activity'

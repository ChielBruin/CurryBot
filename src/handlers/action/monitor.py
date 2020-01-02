from datetime import datetime

from ..messageHandler import MessageHandler
from data import Cache, Logger
from configResponse import Send, Done, AskChild, AskCacheKey, CreateException


class ActivityMonitor (MessageHandler):
    def __init__(self, log_chat, log_user, cache_key):
        super(ActivityMonitor, self).__init__([])
        self.cache_key = cache_key
        self.log_user = log_user
        self.log_chat = log_chat

    def on_update(self, bot):
        if not Cache.contains(self.cache_key):
            Cache.put(self.cache_key, {})

    def call(self, bot, message, target, exclude):
        time = datetime.now().timestamp()
        if self.log_chat:
            chat_id = str(message.chat.id)
            Cache.put([self.cache_key, 'chat', chat_id], time)

        if self.log_user:
            user_id = str(message.from_user.id)
            Cache.put([self.cache_key, 'user', user_id], time)

        return []

    def has_effect():
        return True

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            default = {'chat':{}, 'user':{}}
            return (1, None, AskCacheKey(default))
        elif stage == 1 and arg:
            return (2, arg, Send('Should the chat activity be monitored?', buttons=Send.YES_NO))
        elif stage == 2:
            if isinstance(arg, str):
                return (3, (data, arg), Send('Should user activity be monitored?', buttons=Send.YES_NO))
            else:
                return (2, arg, Send('There are just two options, and those are provided by these buttons:', buttons=Send.YES_NO))
        elif stage == 3:
            if isinstance(arg, str):
                return (-1, None, Done(ActivityMonitor(data[1], arg, data[0])))
            else:
                return (3, arg, Send('That is not equivalent to pressing the buttons', buttons=Send.YES_NO))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for monitor')

    def _to_dict(self):
        return {'key': self.cache_key, 'log_chat': self.log_chat, 'log_user': self.log_user}

    @classmethod
    def _from_dict(cls, dict, children):
        return ActivityMonitor(dict['log_chat'], dict['log_user'], dict['key'])

    @classmethod
    def get_name(cls):
        return 'Log chat or user activity'

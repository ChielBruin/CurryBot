from datetime import datetime, timedelta
import re

from data import Cache
from ..messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, AskCacheKey, NoChild, CreateException


class AbstractNoActivity (MessageHandler):
    def __init__(self, cache_key, timedelta, children):
        super(AbstractNoActivity, self).__init__(children)
        self.timedelta = timedelta
        self.cache_key = cache_key

    def _call(self, monitor_type, id, bot, msg, target, exclude):
        time = datetime.now()

        cached = Cache.get([self.cache_key, monitor_type, str(id)])
        if cached:
            last_activity = datetime.fromtimestamp(cached)
        else:
            last_activity = datetime.fromtimestamp(0)

        if (last_activity + self.timedelta) <= time:
            Cache.put([self.cache_key, monitor_type, str(id)], time.timestamp())
            return self.propagate(bot, msg, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            default = {'chat':{}, 'user':{}}
            return (1, None, AskCacheKey(default))
        elif stage == 1 and arg:
            return (2, arg, Send('Send me the amout of minutes of inactivity'))
        elif stage == 2:
            if arg.text and re.match(r'[\d]+$', arg.text):
                minutes = int(arg.text)
                return (3, (data, minutes, []), AskChild())
            else:
                return (2, arg, Send('Invalid input, try again'))
        elif stage == 3:
            if isinstance(arg, MessageHandler):
                data[2].append(arg)
                return (3, data, AskChild())
            else:
                key, minutes, children = data
                return (-1, None, Done(cls._from_dict({'key': key, 'timedelta': (0, minutes * 60)}, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for activity')

    def _to_dict(self):
        td = self.timedelta
        return {'key': self.cache_key, 'timedelta': (td.days, td.seconds)}


class ChatNoActivity (AbstractNoActivity):
    def __init__(self, timedelta, cache_key, children):
        super(ChatNoActivity, self).__init__(timedelta, cache_key, children)

    def call(self, bot, msg, target, exclude):
        return self._call('chat', msg.chat.id, bot, msg, target, exclude)

    @classmethod
    def get_name(cls):
        return "Chat inactive for time"

    @classmethod
    def _from_dict(cls, dict, children):
        days, seconds = dict['timedelta']
        return ChatNoActivity(dict['key'], timedelta(days=days, seconds=seconds), children)


class UserNoActivity (AbstractNoActivity):
    def __init__(self, timedelta, cache_key, children):
        super(UserNoActivity, self).__init__(timedelta, cache_key, children)

    def call(self, bot, msg, target, exclude):
        return self._call('user', msg.from_user.id,  bot, msg, target, exclude)

    @classmethod
    def get_name(cls):
        return "User inactive for time"

    @classmethod
    def _from_dict(cls, dict, children):
        days, seconds = dict['timedelta']
        return UserNoActivity(dict['key'], timedelta(days=days, seconds=seconds), children)

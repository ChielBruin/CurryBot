from datetime import datetime

from cache import Cache
from messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, NoChild, CreateException


class AbstractNoActivity (MessageHandler):
    def __init__(self, timedelta, cache_key, reset, children):
        super(AbstractNoActivityFilter, self).__init__(children)
        self.timedelta = timedelta
        self.cache_key = cache_key
        self.reset = reset
        self.initial_time = initial_time

    def _filter(self, message, id, key):
        time = message.date
        id = str(id)

        cached = Cache.shared_get_cache(self.cache_key)
        if key in cached:
            cached_type = cached[key]
            if id in cached_type:
                last_activity = datetime.fromtimestamp(cached_type[id])
            elif not initial_time is None:
                last_activity = self.initial_time
            else:
                return None

            if (last_activity + self.timedelta) <= time:
                if self.reset:
                    cached_type[id] = message.date.timestamp()
                    cached = Cache.shared_put_cache(self.cache_key, cached)
                return message
        return None

    @classmethod
    def is_entrypoint(cls):
        return True

    # @classmethod
    # def create(cls, stage, data, arg):
    #     if stage is 0:
    #         return (1, [], AskChild())
    #     elif stage is 1 and isinstance(arg, MessageHandler):
    #         data.append(arg)
    #         return (1, data, AskChild())
    #     elif stage is 1 and isinstance(arg, NoChild):
    #         return (-1, None, Done(UserJoinedChat(data)))
    #     else:
    #         print(stage, data, arg)
    #         raise CreateException('Invalid create state for userJoinedChat')


class ChatNoActivity (AbstractNoActivity):
    def __init__(self, id, timedelta, cache_key, reset=True, initial_time=None):
        super(ChatNoActivity, self).__init__(id, timedelta, cache_key, reset, initial_time)

    def filter(self, message):
        return self._filter(message, message.chat.id, 'chat')

    @classmethod
    def get_name(cls):
        return "Chat inactive for time"


class UserNoActivity (AbstractNoActivity):
    def __init__(self, id, timedelta, cache_key, reset=True, initial_time=None):
        super(UserNoActivity, self).__init__(id, timedelta, cache_key, reset, initial_time)

    def filter(self, message):
        return self._filter(message.date, message.from_user.id, 'user')

    @classmethod
    def get_name(cls):
        return "User inactive for time"

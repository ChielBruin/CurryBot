from datetime import datetime

from filter.filter import Filter
from cache import Cache


class AbstractNoActivityFilter (Filter):
    def __init__(self, id, timedelta, cache_key, reset, initial_time):
        super(AbstractNoActivityFilter, self).__init__(id)
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


class ChatNoActivityFilter (AbstractNoActivityFilter):
    def __init__(self, id, timedelta, cache_key, reset=True, initial_time=None):
        super(ChatNoActivityFilter, self).__init__(id, timedelta, cache_key, reset, initial_time)

    def filter(self, message):
        return self._filter(message, message.chat.id, 'chat')


class UserNoActivityFilter (AbstractNoActivityFilter):
    def __init__(self, id, timedelta, cache_key, reset=True, initial_time):
        super(UserNoActivityFilter, self).__init__(id, timedelta, cache_key, reset, initial_time)

    def filter(self, message):
        return self._filter(message.date, message.from_user.id, 'user')

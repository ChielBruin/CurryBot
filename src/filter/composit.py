from filter.filter import Filter

import random

class NoFilter (Filter):
    def filter(self, message):
        return message

class ParameterizeFilter (Filter):
    def __init__(self, id, parameter):
        super(ParameterizeFilter, self).__init__(id)
        self._parameter = parameter

    def filter(self, message):
        message.text = str(self._parameter)
        return message

class PercentageFilter (Filter):
    def __init__(self, id, percentage):
        super(PercentageFilter, self).__init__(id)
        self._percentage = percentage

    def filter(self, message):
        if random.randrange(100) <= self._percentage:
            return message
        else:
            return None


class AndFilter (Filter):
    def __init__(self, id, filters):
        super(AndFilter, self).__init__(id)
        self._filters = filters

    def update(self):
        for filter in self._filters:
            filter.update()

    def filter(self, message):
        for filter in self._filters:
            message = filter.filter(message)
            if not message:
                return None
        return message


class OrFilter (Filter):
    def __init__(self, id, filters):
        super(OrFilter, self).__init__(id)
        self._filters = filters

    def update(self):
        for filter in self._filters:
            filter.update()

    def filter(self, message):
        for filter in self._filters:
            msg = filter.filter(message)
            if msg:
                return msg
        return None

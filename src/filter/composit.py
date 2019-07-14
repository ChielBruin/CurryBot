from filter.filter import Filter

import random

class NoFilter (Filter):
    def filter(self, message):
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
    def __init__(self, id, left, right):
        super(AndFilter, self).__init__(id)
        self._left = left
        self._right = right

    def update(self):
        self._left.update()
        self._right.update()

    def filter(self, message):
        l_msg = self._left.filter(message)
        if l_msg:
            return self._right.filter(l_msg)
        else:
            return None


class OrFilter (Filter):
    def __init__(self, id, left, right):
        super(OrFilter, self).__init__(id)
        self._left = left
        self._right = right

    def update(self):
        self._left.update()
        self._right.update()

    def filter(self, message):
        l_msg = self._left.filter(message)
        if l_msg:
            return l_msg
        else:
            return self._right.filter(message)

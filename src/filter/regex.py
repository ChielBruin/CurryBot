import re

from messageHandler import MessageHandler
from exceptions import FilterException

class AbstractRegexFilter (MessageHandler):
    def __init__(self, regex, children, group=None):
        super(AbstractRegexFilter, self).__init__(children)
        self._regex = re.compile(regex)
        self._group = group

    def call(self, bot, message, target, exclude):
        if message.text is None:
            raise FilterException()

        match = self.matcher(self._regex, message.text)
        if match:
            if self._group:
                message.text = match.group(self._group)
            self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    def matcher(self, regex, text):
        raise Exception('Not implemented')

class MatchFilter (AbstractRegexFilter):
    def matcher(self, regex, text):
        return re.match(self._regex, text)

class SearchFilter (AbstractRegexFilter):
    def matcher(self, regex, text):
        return re.search(self._regex, text)

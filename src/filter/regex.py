import re

from filter.filter import Filter


class AbstractRegexFilter (Filter):
    def __init__(self, id, regex, group=None):
        super(AbstractRegexFilter, self).__init__(id)
        self._regex = re.compile(regex)
        self._group = group

    def filter(self, message):
        if message.text is None:
            return None

        match = self.matcher(self._regex, message.text)
        if match:
            if self._group:
                message.text = match.group(self._group)
            return message
        else:
            return None

    def matcher(self, regex, text):
        raise Exception('Not implemented')

class MatchFilter (AbstractRegexFilter):
    def matcher(self, regex, text):
        return re.match(self._regex, text)

class SearchFilter (AbstractRegexFilter):
    def matcher(self, regex, text):
        return re.search(self._regex, text)

class CommandFilter (MatchFilter):
    def __init__(self, id, command):
        regex = '/%s([\s].*)?$' % (command)
        super(CommandFilter, self).__init__(id, regex)

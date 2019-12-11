import re

from ..messageHandler import MessageHandler
from exceptions import FilterException

from configResponse import Send, Done, AskChild, NoChild, CreateException
from telegram import InlineKeyboardButton, Message

class AbstractRegexFilter (MessageHandler):
    def __init__(self, regex, children=[], group=None):
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
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    def matcher(self, regex, text):
        raise Exception('Not implemented')

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, Send('Send me the regex to match'))
        elif stage is 1 and arg:
            if arg.text:
                try:
                    pattern = re.compile(arg.text)
                    groups = list(range(pattern.groups + 1)) + list(pattern.groupindex.keys())
                    if len(groups) > 1:
                        buttons = [[InlineKeyboardButton(text=str(group), callback_data='r_' + str(group))] for group in groups]
                        msg = 'Select a captured group to replace the original message, select group 0 to retain the entire match'
                        return (2, arg.text, Send(msg=msg, buttons=buttons))
                    else:
                        return (3, (arg.text, None, []), AskChild())
                except re.error:
                    return (1, None, Send('Invalid expression, try again'))
            else:
                return (1, data, Send('Please send text and nothing else'))
        elif stage is 2 and arg:
            if isinstance(arg, Message):
                raise CreateException() #TODO: resend the buttons
            arg = arg[2:]
            try:
                group = int(arg)
                if group < 0:
                    group = None
            except:
                group = arg
            return (3, (data, group, []), AskChild())
        elif stage is 3 and isinstance(arg, MessageHandler):
            data[2].append(arg)
            return (3, data, AskChild())
        elif stage is 3 and isinstance(arg, NoChild):
            regex, group, children = data
            return (-1, None, Done(cls._create(regex, children, group)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for regexFilter')

    def _to_dict(self):
        return {'group': self._group, 'regex': self._regex.pattern}


class MatchFilter (AbstractRegexFilter):
    def matcher(self, regex, text):
        return re.match(self._regex, text)

    @classmethod
    def get_name(cls):
        return "Match text with regex"

    @classmethod
    def _create(cls, regex, children, group):
        return MatchFilter(regex, children, group)

    @classmethod
    def _from_dict(cls, dict, children):
        regex = dict['regex']
        group = dict['group']
        return MatchFilter(regex, children, group=group)


class SearchFilter (AbstractRegexFilter):
    def matcher(self, regex, text):
        return re.search(self._regex, text)

    @classmethod
    def get_name(cls):
        return "Search text for regex"

    @classmethod
    def _create(cls, regex, children, group):
        return SearchFilter(regex, children, group)

    @classmethod
    def _from_dict(cls, dict, children):
        regex = dict['regex']
        group = None if dict['group'] == 'None' else dict['group']
        return SearchFilter(regex, children, group=group)

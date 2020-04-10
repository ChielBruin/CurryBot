import re

from telegram import MessageEntity

from currybot.handlers.messageHandler import MessageHandler
from currybot.exceptions import FilterException
from currybot.configResponse import Send, Done, AskChild, NoChild, CreateException


class IsCommand(MessageHandler):
    def __init__(self, cmd, children):
        super(IsCommand, self).__init__(children)
        self._command = cmd

    def call(self, bot, message, target, exclude):
        commands = list(filter(lambda e: e.type == MessageEntity.BOT_COMMAND, message.entities))
        if commands:   # TODO: add check if there is no mention of an other bot
            match = re.match(self._command, message.text)
            if match:
                return self.propagate(bot, message, target, exclude)
        raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return 'Message is command'

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, Send('Please send me the command you want to filter on'))
        elif stage == 1 and arg:
            if not arg.text or not re.match(r'/[\w]+$', arg.text):
                return (1, None, Send('Not a valid command, try again'))
            command = arg.text[1:]
            return (2, (command, []), AskChild())
        elif stage == 2 and isinstance(arg, MessageHandler):
            data[1].append(arg)
            return (2, data, AskChild())
        elif stage == 2 and isinstance(arg, NoChild):
            (command, children) = data
            return (-1, None, Done(IsCommand('/' + command, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for commandHandler')

    @classmethod
    def _from_dict(cls, dict, children):
        return IsCommand(dict['regex'], children)

    def _to_dict(self):
        return {'regex': self._command}

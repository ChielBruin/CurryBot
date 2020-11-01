from currybot.handlers.messageHandler import MessageHandler
from currybot.exceptions import FilterException
from currybot.configResponse import Send, Done, AskChild, NoChild, CreateException
import requests, re


class IsValidUrl(MessageHandler):
    def __init__(self, children):
        super(IsValidUrl, self).__init__(children)

    def call(self, bot, message, target, exclude):
        url = message.text if re.match('https?://', message.text) else 'http://%s' % message.text
        response = requests.head(url, allow_redirects=True)
        
        if response.status_code < 400:
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Message is existing website"

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], AskChild())
        elif stage == 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage == 1 and isinstance(arg, NoChild):
            return (-1, None, Done(IsValidUrl(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for isValidUrl')

    @classmethod
    def _from_dict(cls, dict, children):
        return IsValidUrl(children)

    def _to_dict(self):
        return {}

from ..messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, NoChild, CreateException


class SenderUsername (MessageHandler):
    def __init__(self, show_first_name, show_last_name, show_handle, children):
        super(SenderUsername, self).__init__(children)
        self.show_first_name = show_first_name
        self.show_last_name = show_last_name
        self.show_handle = show_handle

    def call(self, bot, message, target, exclude):
        user = message.from_user
        if self.show_first_name:
            first_name = user.first_name
        else:
            first_name = None

        if self.show_last_name and user.last_name:
            last_name = user.last_name
        else:
            last_name = None

        if self.show_handle and user.username:
            handle = ' @%s' % user.username
        else:
            handle = None

        message.text = ' '.join(filter(lambda x: not x is None, [first_name, last_name, handle]))
        return self.propagate(bot, message, target, exclude)

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Set username as message text"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, Send('Should the first name be shown?', buttons=Send.YES_NO))
        elif stage is 1 and arg:
            if isinstance(arg, Message):
                return (1, data, Send('Please reply by clicking the buttons', buttons=Send.YES_NO))
            else:
                return (2, arg == 'yes', Send('Should the last name be shown?', buttons=Send.YES_NO))
        elif stage is 2 and arg:
            if isinstance(arg, Message):
                return (2, data, Send('Please reply by clicking the buttons', buttons=Send.YES_NO))
            else:
                return (3, (data, arg == 'yes'), Send('Should the username be shown?', buttons=Send.YES_NO))
        elif stage is 3 and arg:
            if isinstance(arg, Message):
                return (3, data, Send('Please reply by clicking the buttons', buttons=Send.YES_NO))
            else:
                first, last = data
                return (4, (first, last, (arg == 'yes'), []), AskChild())
        elif stage is 4:
            if isinstance(arg, MessageHandler):
                data[3].append(arg)
                return (4, data, AskChild())
            else:
                first, last, handle, children = data
                return (-1, None, Done(SenderUsername(first, last, handle, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendTextMessage')

    @classmethod
    def _from_dict(cls, dict, children):
        return SenderUsername(children, dict['show_handle'])

    def _to_dict(self):
        return {'show_handle': self.show_handle}

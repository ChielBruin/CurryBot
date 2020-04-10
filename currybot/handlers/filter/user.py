from currybot.handlers.messageHandler import MessageHandler
from currybot.exceptions import FilterException
from currybot.data import Cache
from currybot.configResponse import Send, Done, AskChild, NoChild, CreateException


class SenderIsBotAdmin(MessageHandler):
    def __init__(self, children):
        super(SenderIsBotAdmin, self).__init__(children)

    def call(self, bot, message, target, exclude):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if Cache.is_chat_admin(chat_id, user_id):
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Sender is bot admin"

    @classmethod
    def _from_dict(cls, dict, children):
        return SenderIsBotAdmin(children)

    def _to_dict(self):
        return {}

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], AskChild())
        elif stage == 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage == 1 and isinstance(arg, NoChild):
            return (-1, None, Done(SenderIsBotAdmin(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for SenderIsBotAdmin')


class IsFrom(MessageHandler):
    def __init__(self, user_id, children):
        super(IsFrom, self).__init__(children)
        self.user_id = user_id

    def call(self, bot, message, target, exclude):
        if self.user_id == message.from_user.id:
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "From a certain user"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsFrom(dict['user_id'], children)

    def _to_dict(self):
        return {'user_id': self.user_id}

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, Send('Forward me a message from the user you want to filter on'))
        elif stage == 1:
            if arg.from_user:
                return (2, (arg.from_user.id, []), AskChild())
            else:
                return (1, None, Send('That is not what I asked you to do, try again'))
        elif stage == 2 and isinstance(arg, MessageHandler):
            data[1].append(arg)
            return (2, data, AskChild())
        elif stage == 2 and isinstance(arg, NoChild):
            return (-1, None, Done(IsFrom(data[0], data[1])))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for isFrom')

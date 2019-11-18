import re
from telegram import MessageEntity

from logger         import Logger
from messageHandler import MessageHandler
from exceptions     import FilterException
from config         import Config

from configResponse import Send, Done, AskChild, NoChild, CreateException


class UserJoinedChat (MessageHandler):
    def __init__(self, children):
        super(UserJoinedChat, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.new_chat_members:
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Someone joined the chat"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(UserJoinedChat(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for userJoinedChat')

class IsReply (MessageHandler):
    def __init__(self, children):
        super(IsReply, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.reply_to_message:
            self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Message is reply"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(IsReply(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for isReply')


class CommandFilter (MessageHandler):
    def __init__(self, cmd, children):
        super(CommandFilter, self).__init__(children)
        self._command = r'/' + cmd

    def call(self, bot, message, target, exclude):
        commands = list(filter(lambda e: e.type == MessageEntity.BOT_COMMAND, message.entities))
        if len(commands) > 0:   # TODO: add check if there is no mention of an other bot
            match = re.match(self._command, message.text)
            if match:
                return self.propagate(bot, message, target, exclude)
        raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def get_name(cls):
        return "Message is command"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, Send("Please send me the command you want to filter on"))
        elif stage is 1 and arg:
            if not arg.text or not re.match(r'/[\w]+$', arg.text):
                return (1, None, Send("Not a valid command"))
            command = arg.text[1:]
            return (2, (command, []), AskChild())
        elif stage is 2 and isinstance(arg, MessageHandler):
            data[1].append(arg)
            return (2, data, AskChild())
        elif stage is 2 and isinstance(arg, NoChild):
            (command, children) = data
            return (-1, None, Done(CommandFilter(command, children)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for commandHandler')


class SenderIsBotAdmin (MessageHandler):
    def __init__(self, children):
        super(SenderIsBotAdmin, self).__init__(children)

    def call(self, bot, message, target, exclude):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if Config.is_chat_admin(chat_id, user_id):
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
        print(42, self.children)
        return {}

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, [], AskChild())
        elif stage is 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage is 1 and isinstance(arg, NoChild):
            return (-1, None, Done(SenderIsBotAdmin(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for SenderIsBotAdmin')

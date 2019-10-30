import re
from telegram import MessageEntity

from logger         import Logger
from messageHandler import MessageHandler
from exceptions     import FilterException


class SelfJoinedChat (MessageHandler):
    def __init__(self, children):
        super(SelfJoinedChat, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.new_chat_members:
            try:
                next(filter(lambda usr: usr.id == bot.id, message.new_chat_members))
                return self.propagate(bot, message, target, exclude)
            except StopIteration as e:
                raise FilterException()
        else:
            raise FilterException()

class UserJoinedChat (MessageHandler):
    def __init__(self, children):
        super(SelfJoinedChat, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.new_chat_members:
            self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

class IsReply (MessageHandler):
    def __init__(self, children):
        super(IsReply, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.reply_to_message:
            self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

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

class InPrivateChat (MessageHandler):
    def __init__(self, children):
        super(InPrivateChat, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if(message.chat.type == 'private'):
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

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

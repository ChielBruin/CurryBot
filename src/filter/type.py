import re
from telegram import MessageEntity

from logger         import Logger
from messageHandler import MessageHandler
from exceptions     import FilterException


class IsReply (MessageHandler):
    def __init__(self, children):
        super(IsReply, self).__init__(children)

    def call(self, bot, message, target, exclude):
        if message.reply_to_message:
            self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

class InChat (MessageHandler):
    def __init__(self, chat_id, children):
        super(InChat, self).__init__(children)
        self.chat_id = chat_id

    def call(self, bot, message, target, exclude):
        if message.chat.id == self.chat_id:
            return self.propagate(bot, message, target, exclude)
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
    def __init__(self, admins, children):
        super(SenderIsBotAdmin, self).__init__(children)
        self._admins = admins

    def call(self, bot, message, target, exclude):
        chat_id = message.chat.id

        if chat_id in self._admins:
            chat_admins = self._admins[chat_id]
        else:
            chat_admins = []
            Logger.log_error(msg='No admin for chat with id %d' % chat_id)

        if message.from_user.id in chat_admins:
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

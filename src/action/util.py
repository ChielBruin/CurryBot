from messageHandler import MessageHandler
from logger import Logger
from config import Config

class ShowInfo (MessageHandler):
    def __init__(self):
        super(ShowInfo, self).__init__([])

    def call(self, bot, msg, target, exclude):
        text = self.analyze_message(msg, bot)
        bot.send_message(
                    chat_id=msg.chat.id,
                    text=text,
                    parse_mode='Markdown',
                    reply_to_message_id=target
        )
        return []

    def analyze_message(self, message, bot):
        Logger.log_info('Info command used:')
        Logger.log_info('Chat_id: %s' % str(message.chat.id))
        if message.reply_to_message:
            message = message.reply_to_message
            if message.sticker:
                sticker = message.sticker
                Logger.log_debug('Sticker_id: %s' % sticker.file_id)
                Logger.log_debug('Pack_id: %s' % sticker.set_name)
                return 'That is a sticker'
            elif message.forward_from:
                Logger.log_debug('Forwarded message')
                Logger.log_debug('Message_id: %d' % message.message_id)
                return 'That is a forwarded message'
            else:
                Logger.log_debug(str(message))
                return 'That is a message'
        else:
            return 'I\'m %s and I reply to your messages when I feel the need to.' % bot.first_name


class ForceUpdate (MessageHandler):
    def __init__(self, bot):
        super(ForceUpdate, self).__init__([])
        self.bot = bot

    def call(self, bot, msg, target, exclude):
        self.bot.update_cache()
        return []


class MakeSenderAdmin (MessageHandler):
    def __init__(self):
        super(MakeSenderAdmin, self).__init__([])

    def call(self, bot, msg, target, exclude):
        Config.add_chat_admin(msg.chat.id, msg.from_user.id)
        return []


class MakeSenderAdmin (MessageHandler):
    def __init__(self):
        super(MakeSenderAdmin, self).__init__([])

    def call(self, bot, msg, target, exclude):
        Config.add_chat_admin(msg.chat.id, msg.from_user.id)
        return []

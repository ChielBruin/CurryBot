from action.action import Action
from logger import Logger

class InfoAction (Action):

    def __init__(self, id, bot):
        super(InfoAction, self).__init__(id)
        self.bot = bot

    def dispatch(self, bot, msg, exclude):
        text = self.analyze_message(msg)
        bot.send_message(chat_id=msg.chat.id, text=text, parse_mode='Markdown')
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        text = self.analyze_message(msg)
        bot.send_message(chat_id=msg.chat.id, text=text, reply_to_message_id=reply_to, parse_mode='Markdown')
        return []

    def analyze_message(self, message):
        Logger.log('INFO', 'Info command used:')
        Logger.log('INFO', 'Chat_id: %s' % str(message.chat.id))
        if message.reply_to_message:
            message = message.reply_to_message
            if message.sticker:
                sticker = message.sticker
                Logger.log('DEBUG', 'Sticker_id: %s' % sticker.file_id)
                Logger.log('DEBUG', 'Pack_id: %s' % sticker.set_name)
                return 'That is a sticker'
            elif message.forward_from:
                Logger.log('DEBUG', 'Forwarded message')
                Logger.log('DEBUG', 'Message_id: %d' % message.message_id)
                return 'That is a forwarded message'
            else:
                Logger.log('DEBUG', str(message))
                return 'That is a message'
        else:
            return '`putStrLn "Hello, World!"``\nI reply to your messages when I feel the need to.'


class UpdateAction (Action):
    def __init__(self, id, bot):
        super(UpdateAction, self).__init__(id)
        self.bot = bot

    def dispatch(self, bot, msg, exclude):
        self.bot.update_cache()
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        self.bot.update_cache()
        return []

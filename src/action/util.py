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
            return '`putStrLn "Hello, World!"`\nI reply to your messages when I feel the need to.'


class UpdateAction (Action):
    def __init__(self, id, bot):
        super(UpdateAction, self).__init__(id)
        self.bot = bot

    def do_update(self):
        Logger.log_info('Update command used')
        self.bot.update_cache()

    def dispatch(self, bot, msg, exclude):
        self.do_update()
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        self.do_update()
        return []

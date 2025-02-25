from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message

from currybot.configResponse import Send, Done, CreateException
from currybot.data import Cache
from currybot.handlers.messageHandler import RandomMessageHandler


class AbstractSendMessage(RandomMessageHandler):
    def __init__(self, messages, show_preview, buttons, parse_mode):
        super(AbstractSendMessage, self).__init__(RandomMessageHandler.get_random_id(), [])
        self.add_options(messages)
        self.parse_mode = parse_mode
        self.show_preview = show_preview
        self.buttons = buttons
        Cache.config_entry(self._id, False)

    def apply_message(self, message, reply_text):
        """
        Given the original message and the reply text pattern,
        try filling in the holes in the reply pattern.
        """
        user = message.from_user
        if '%h' in reply_text and user.username:
            reply_text = reply_text.replace('%h', user.username)
        if '%f' in reply_text and user.first_name:
            reply_text = reply_text.replace('%f', user.first_name)
        if '%l' in reply_text and user.last_name:
            reply_text = reply_text.replace('%l', user.last_name)
        if '%n' in reply_text and user.first_name:
            name = '%s %s' % (user.first_name, user.last_name) if user.last_name else user.first_name
            reply_text = reply_text.replace('%n', name)
        if '%s' in reply_text:
            reply_text = reply_text % message.text

        return reply_text

    def call(self, bot, msg, target, exclude):
        if msg.text is None:
            msg.text = ''

        msg_data = msg.text[:64] if len(msg.text) > 64 else msg.text
        (id, message) = self.select_random_option(exclude=exclude)
        applied_message = self.apply_message(msg, message)

        if self.buttons:
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(text=text, callback_data=text) for text in button_row] for button_row in self.buttons])
        else:
            buttons = None

        bot.send_message(chat_id=msg.chat.id,
                         text=applied_message,
                         reply_to_message_id=target,
                         parse_mode=self.parse_mode,
                         disable_web_page_preview=not self.show_preview,
                         reply_markup=buttons)
        return [id]

    def has_effect(self):
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def create(cls, stage, data, arg):
        buttons = [[InlineKeyboardButton(text='horizontal', callback_data='horizontal'), InlineKeyboardButton(text='vertical', callback_data='vertical')]]
        if stage == 0:
            return (1, None, Send('Please send me the text to reply'))
        elif stage == 1 and arg:
            if not arg.text:
                return (1, None, Send('Please reply with text, not with something else'))
            return (2, arg.text, Send('Should previews be shown for URLs?', buttons=Send.YES_NO))
        elif stage == 2 and arg:
            if isinstance(arg, Message):
                return (2, data, Send('Please reply by clicking the buttons', buttons=Send.YES_NO))
            else:
                return (3, (data, arg == 'yes'), Send('Do you want to show buttons?', buttons=Send.YES_NO))
        elif stage == 3:
            if arg == 'yes':
                return (4, data, Send('Should the buttons be horizontal of vertical?', buttons=buttons))
            else:
                message, url = data
                obj = cls._from_dict({'messages': [message], 'preview': url, 'buttons': None}, [])
                return (-1, None, Done(obj))
        elif stage == 4:
            if isinstance(arg, str):
                return (5, (data, arg == 'horizontal', []), Send('Now send me the text for the button'))
            else:
                return (4, data, Send('I created those buttons for a reason', buttons=buttons))
        elif stage == 5:
            if arg.text:
                data[2].append(arg.text)
                return (6, data, Send('Dou you want to add more buttons?', buttons=Send.YES_NO))
            else:
                return (5, data, Send('Invalid message, it should contain text'))
        elif stage == 6:
            if isinstance(arg, str):
                if arg == 'yes':
                    return (5, data, Send('Send me the text for the next button'))
                else:
                    ((text, url), is_horizontal, buttons) = data
                    if is_horizontal:
                        buttons = [buttons]
                    else:
                        buttons = [[button] for button in buttons]
                    obj = cls._from_dict({'messages': [text], 'preview': url, 'buttons': buttons}, [])
                    return (-1, None, Done(obj))
            else:
                return (4, data, Send('I know you are a smart kid, but that was not a button press', buttons=Send.YES_NO))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendTextMessage')

    def _to_dict(self):
        return {'messages': self.list_options(), 'preview': self.show_preview, 'buttons': self.buttons}


class SendTextMessage(AbstractSendMessage):
    def __init__(self, message, show_preview, buttons):
        super(SendTextMessage, self).__init__(message, show_preview, buttons, parse_mode=None)

    @classmethod
    def get_name(cls):
        return 'Send a message'

    @classmethod
    def _from_dict(cls, dict, children):
        return SendTextMessage(dict['messages'], dict['preview'], dict['buttons'])


class SendMarkdownMessage(AbstractSendMessage):
    def __init__(self, message, show_preview, buttons):
        super(SendMarkdownMessage, self).__init__(message, show_preview, buttons, parse_mode='Markdown')

    @classmethod
    def get_name(cls):
        return "Send Markdown formatted message"

    @classmethod
    def _from_dict(cls, dict, children):
        return SendMarkdownMessage(dict['messages'], dict['preview'], dict['buttons'])


class SendHTMLMessage(AbstractSendMessage):
    def __init__(self, message, show_preview, buttons):
        super(SendHTMLMessage, self).__init__(message, show_preview, buttons, parse_mode='HTML')

    @classmethod
    def get_name(cls):
        return "Send HTML formatted message"

    @classmethod
    def _from_dict(cls, dict, children):
        return SendHTMLMessage(dict['messages'], dict['preview'], dict['buttons'])

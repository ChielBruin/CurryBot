from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..messageHandler import MessageHandler
from configResponse import Send, Done, AskChild, CreateException


class SendButtons (MessageHandler):
    def __init__(self, text, buttons):
        super(SendButtons, self).__init__([])
        self.text = text
        self.buttons = buttons

    def call(self, bot, msg, target, exclude):
        msg_data = msg.text[:47] if len(msg.text) > 47 else msg.text
        text = self.text % msg.text if '%s' in self.text else self.text

        buttons = [[InlineKeyboardButton(text=text, callback_data='%s_%s' % (text, msg_data)) for text in button_row] for button_row in self.buttons]
        bot.send_message(chat_id=msg.chat.id,
                         text=text,
                         reply_to_message_id=target,
                         reply_markup=InlineKeyboardMarkup(buttons))
        return []

    def has_effect():
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Send buttons"

    @classmethod
    def create(cls, stage, data, arg):
        buttons = [[InlineKeyboardButton(text='horizontal', callback_data='horizontal'), InlineKeyboardButton(text='vertical', callback_data='vertical')]]
        if stage == 0:
            return (1, None, Send('Please send a message to send.'))
        elif stage == 1:
            if arg.text:
                return (2, arg.text, Send('Should the buttons be horizontal of vertical?', buttons=buttons))
            else:
                return (1, None, Send('I said message, not whatever you just sent me'))
        elif stage == 2:
            if isinstance(arg, str):
                return (3, (data, arg=='horizontal', []), Send('Now send me the text for the button'))
            else:
                return (2, data, Send('I created those buttons for a reason', buttons=buttons))
        elif stage == 3:
            if arg.text and len(arg.text) < 16 and '_' not in arg.text:
                data[2].append(arg.text)
                return (4, data, Send('Dou you want to add more buttons?', buttons=Send.YES_NO))
            else:
                return (3, None, Send('Invalid message, either it has no text, it contains an underscore or it is longer than 16 characters'))
        elif stage == 4:
            if isinstance(arg, str):
                if arg=='yes':
                    return (3, data, Send('Send me the text for the next button'))
                else:
                    (text, is_horizontal, buttons) = data
                    if is_horizontal:
                        buttons = [buttons]
                    else:
                        buttons = [[button] for button in buttons]
                    return (-1, None, Done(SendButtons(text, buttons)))
            else:
                return (4, data, Send('I know you are a smart kid, but that was not a button press', buttons=Send.YES_NO))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendButtons')

    def _to_dict(self):
        return {'text': self.text, 'buttons': self.buttons}

    @classmethod
    def _from_dict(cls, dict, children):
        return SendButtons(dict['text'], dict['buttons'])

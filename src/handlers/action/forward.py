from ..messageHandler import MessageHandler
from configResponse import Send, Done, AskChild, CreateException


class Forward (MessageHandler):
    '''
    An action that forwards a message.
    '''

    def __init__(self, chat_id, msg_id):
        '''
        Load all the messages from the given config
        '''
        super(Forward, self).__init__([])
        self.chat_id = chat_id
        self.msg_id = msg_id

    def call(self, bot, msg, target, exclude):
        if target:
            raise Exception('You cannot reply using a forwarded message')
        bot.forward_message(chat_id=msg.chat.id, from_chat_id=self.chat_id, message_id=self.msg_id)
        return [self.msg_id]

    @classmethod
    def is_entrypoint(cls):
        return False

    def has_effect():
        return True

    @classmethod
    def get_name(cls):
        return "Forward a message"

    def _to_dict(self):
        return {'chat_id': self.chat_id, 'msg_id': self.msg_id}

    @classmethod
    def _from_dict(cls, dict, children):
        return Forward(dict['chat_id'], dict['msg_id'])

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, Send('Please forward the message to forward'))
        elif stage is 1 and arg:
            if not arg.forward_from:
                return (1, None, Send('Please forward a message'))
            return (-1, None, Done(Forward(arg.chat.id, arg.message_id)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendTextMessage')

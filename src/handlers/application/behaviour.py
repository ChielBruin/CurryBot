from telegram import InlineKeyboardButton

from ..messageHandler import MessageHandler
from exceptions     import FilterException

from configResponse import Send, Done, AskChild, NoChild, CreateException


class SendBehaviour (MessageHandler):
    SEND, REPLY, TRANSATIVE_REPLY = range(3)

    def __init__(self, message, reply, forward, children):
        super(SendBehaviour, self).__init__(children)
        self.message = message
        self.reply = reply
        self.forward = forward


    def call(self, bot, msg, target, exclude):
        if msg.reply_to_message:
            behaviour = self.reply
        elif msg.forward_from:
            behaviour = self.forward
        else:
            behaviour = self.message

        for action in behaviour:
            if action == self.SEND:
                target = None
            elif action == self.REPLY:
                target = msg.message_id
            elif action == self.TRANSATIVE_REPLY:
                target = msg.reply_to_message.message_id
            else:
                raise Exception('Invalid action id %d' % action)

            exclude.extend(self.propagate(bot, msg, target, exclude))
        return exclude

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Change the reply behaviour"

    @classmethod
    def create(cls, stage, data, arg):
        buttons1 = [[InlineKeyboardButton(text='Send', callback_data='b%d'%cls.SEND)], [InlineKeyboardButton(text='Reply', callback_data='b%d'%cls.REPLY)], [InlineKeyboardButton(text='None', callback_data='none')]]
        buttons2 = [[InlineKeyboardButton(text='Transitive', callback_data='b%d'%cls.TRANSATIVE_REPLY)]] + buttons1

        def to_desc(data):
            def from_int(int):
                if int == cls.SEND:
                    return 'send'
                elif int == cls.REPLY:
                    return 'reply'
                elif int == cls.TRANSATIVE_REPLY:
                    return 'transitive'
                else:
                    raise Exception('Unknown behaviour %d' % int)
            return ' -> '.join(map(from_int, data))

        if stage == 0:
            return (1, [], Send('How should the bot behave on a normal message?', buttons=buttons1))
        if stage == 1:
            if isinstance(arg, str):
                if arg == 'none':
                    return (2, (data, []), Send('How should the bot behave on a reply?', buttons=buttons2))
                data.append(int(arg[1]))
                return (1, data, Send('Should it do more? (%s)' % to_desc(data), buttons=buttons1))
        if stage == 2:
            if isinstance(arg, str):
                if arg == 'none':
                    return (3, (data[0], data[1], []), Send('How should the bot behave on a forwarded message?', buttons=buttons1))
                data[1].append(int(arg[1]))
                return (2, data, Send('Should it do more? (%s)' % to_desc(data[1]), buttons=buttons2))
        if stage == 3:
            if isinstance(arg, str):
                if arg == 'none':
                    return (4, (data, []), AskChild())
                data[2].append(int(arg[1]))
                return (3, data, Send('Should it do more? (%s)' % to_desc(data[2]), buttons=buttons1))
            else:
                return (1, data, Send('That is not how buttons work', buttons=buttons1))
        if stage == 4:
            if isinstance(arg, MessageHandler):
                data[1].append(arg)
                return (4, data, AskChild())
            else:
                (message, reply, forward), children = data
                return (-1, None, Done(SendBehaviour(message, reply, forward, children)))
        raise CreateException('Invalid create state for sendBehaviour')

    @classmethod
    def _from_dict(cls, dict, children):
        return SendBehaviour(dict['message'], dict['reply'], dict['forward'], children)

    def _to_dict(self):
        return {'message': self.message, 'reply': self.reply, 'forward': self.forward}


class TransitiveReply(SendBehaviour):
    def __init__(self, children):
        super(TransitiveReply, self).__init__([], [self.TRANSATIVE_REPLY], [], children)

    @classmethod
    def get_name(cls):
        return "Transitive reply"

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], AskChild())
        if stage == 1:
            if isinstance(arg, MessageHandler):
                data.append(arg)
                return (1, data, AskChild())
            else:
                return (-1, None, Done(TransitiveReply(data)))
        raise CreateException('Invalid create state for transitiveReply')


class Reply(SendBehaviour):
    def __init__(self, children):
        super(Reply, self).__init__([self.REPLY], [], [], children)

    @classmethod
    def get_name(cls):
        return "Reply"

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], AskChild())
        if stage == 1:
            if isinstance(arg, MessageHandler):
                data.append(arg)
                return (1, data, AskChild())
            else:
                return (-1, None, Done(Reply(data)))
        raise CreateException('Invalid create state for reply')

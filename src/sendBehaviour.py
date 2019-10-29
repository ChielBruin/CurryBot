import copy

from logger import Logger
from messageHandler import MessageHandler

class SendBehaviour (MessageHandler):

    NONE  = 0
    SEND  = 1
    REPLY = 2
    TRANS = 3

    def __init__(self, children, message=[1], reply=[1], forward=[0]):
        super(SendBehaviour, self).__init__(children)
        self._message = message
        self._reply   = reply
        self._forward = forward

    def apply(self, msg):
        for action in self._select_behaviour(msg):
            if action is self.REPLY:
                yield msg.message_id
            elif action is self.TRANS:
                if msg.reply_to_message and msg.reply_to_message.message_id:
                    yield msg.reply_to_message.message_id
            elif action is self.SEND:
                yield None
            elif action is self.NONE:
                continue
            else:
                Logger.log_error('Undefined behaviour action id \'%d\'' % action)

    def _select_behaviour(self, msg):
        if msg.forward_from:
            return self._forward
        elif msg.reply_to_message:
            return self._reply
        else:
            return self._message

    def call(self, bot, message, target, exclude):
        res = []
        for new_target in self.apply(message):
            out = self.propagate(bot, message, new_target, copy.copy(exclude) if copy else exclude)
            res.append(out)
        return res

class Reply (SendBehaviour):
    def __init__(self, children):
        super(Reply, self).__init__(children, message=[SendBehaviour.REPLY], reply=[SendBehaviour.REPLY], forward=[SendBehaviour.REPLY])

class TransReply (SendBehaviour):
    def __init__(self, children):
        super(TransReply, self).__init__(children, message=[SendBehaviour.REPLY], reply=[SendBehaviour.TRANS], forward=[SendBehaviour.REPLY])

class Send (SendBehaviour):
    def __init__(self, children):
        super(Send, self).__init__(children, message=[SendBehaviour.SEND], reply=[SendBehaviour.SEND], forward=[SendBehaviour.SEND])

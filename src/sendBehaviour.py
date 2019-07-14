from logger import Logger


class SendBehaviour (object):
    def __init__(self, message=['send'], reply=['send'], forward=['none']):
        self._message = message
        self._reply   = reply
        self._forward = forward

    def apply(self, msg):
        for action in self._select_behaviour(msg):
            if action == 'reply':
                yield msg.message_id
            elif action == 'transitiveReply':
                if msg.reply_to_message and msg.reply_to_message.message_id:
                    yield msg.reply_to_message.message_id
            elif action == 'send':
                yield None
            elif action == 'none':
                continue
            else:
                Logger.log('ERROR', 'Undefined behaviour action \'%s\'' % action)

    def _select_behaviour(self, msg):
        if msg.forward_from:
            return self._forward
        elif msg.reply_to_message:
            return self._reply
        else:
            return self._message

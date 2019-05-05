import re


MESSAGE = 'message'
REPLY = 'reply'
FORWARD = 'forward'

class ReplyBehaviour (object):
    """
    Class that models the behaviour of replies.
    Selects whether to use a normal reply, a plain message,
    a transitive reply or to skip it.
    """

    def __init__(self, config):
        """
        Uses the default config.
        Updates it with everything in the given config.
        """
        self.config = self.default_config()
        for key in config:
            if config[key].endswith('*'):
                config[key] = config[key][:-1]
            self.config[key] = re.split('\s*->\s*', config[key])

    def select_target(self, message, index):
        """
        Given the message and the reply-index,
        decides what type of reply should be used.
        Returns the selected taget.
        """
        if message.forward_from:
            action = self.from_config(FORWARD, index)
        elif message.reply_to_message:
            action = self.from_config(REPLY, index)
        else:
            action = self.from_config(MESSAGE, index)
        return self._select_target(action, message)

    def _select_target(self, action, msg):
        """
        Get the target given an action.
        """
        if action == 'reply':
            return msg.message_id
        elif action == 'transitiveReply':
            if msg.reply_to_message and msg.reply_to_message.message_id:
                return msg.reply_to_message.message_id
        elif action == 'send':
            return None
        elif action == 'none':
            raise IndexError('Just skip this one')
        else:
            raise Exception('Unknown action: %s' % action)
        return None

    def from_config(self, type, index):
        """
        Get the desired action from the config.
        """
        config = self.config[type]
        return config[min(index, len(config) - 1)]

    @staticmethod
    def default_config():
        """
        The default config of a replyBehaviour instance.
        """
        return {
            MESSAGE: 'reply -> send*',
            REPLY: 'transitiveReply -> send*',
            FORWARD: 'none*'
        }

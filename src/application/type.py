from messageHandler import MessageHandler


class SwapReply (MessageHandler):
    def __init__(self, children):
        super(SwapReply, self).__init__(children)

    def call(self, bot, msg, target, exclude):
        if (msg.forward_from):
            msg.forward_from.reply_to_message = msg           # Store the original so we can get it back
            return self.propagate(bot, msg.forward_from, target, exclude)
        elif msg.reply_to_message:
            msg.reply_to_message.reply_to_message = msg       # Store the original so we can get it back
            return self.propagate(bot, msg.reply_to_message, target, exclude)
        else:
            raise FilterException()

class SwapSender (MessageHandler):
    def __init__(self, children):
        super(SwapSender, self).__init__(children)

    def call(self, bot, msg, target, exclude):
        if (msg.forward_from):
            msg.forward_from.reply_to_message = msg           # Store the original so we can get it back
            return self.propagate(bot, msg.forward_from, target, exclude)
        elif msg.reply_to_message:
            msg.reply_to_message.reply_to_message = msg       # Store the original so we can get it back
            return self.propagate(bot, msg.reply_to_message, target, exclude)
        else:
            raise FilterException()


class ParameterizeText (MessageHandler):
    def __init__(self, parameter, children):
        super(ParameterizeText, self).__init__(children)
        self._parameter = parameter

    def call(self, bot, message, target, exclude):
        message.text = str(self._parameter)
        return self.propagate(bot, message, target, exclude)

from currybot.handlers.messageHandler import MessageHandler
from currybot.configResponse import Done, AskChild, NoChild, CreateException


class AbstractSwap(MessageHandler):
    def __init__(self, children):
        super(AbstractSwap, self).__init__(children)

    def do_swap(self, msg):
        raise Exception('do_swap not implemented')

    def call(self, bot, msg, target, exclude):
        if msg.reply_to_message:
            swapped = self.do_swap(msg)
            return self.propagate(bot, swapped, target, exclude)
        else:
            raise Exception('Message is not a reply')

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], AskChild())
        elif stage == 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage == 1 and isinstance(arg, NoChild):
            return (-1, None, Done(SwapReply(data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for swapReply')

    @classmethod
    def _from_dict(cls, dict, children):
        return SwapReply(children)

    def _to_dict(self):
        return {}


class SwapReply(AbstractSwap):
    @classmethod
    def get_name(cls):
        return "Swap reply messages"

    def do_swap(self, msg):
        msg.reply_to_message.reply_to_message = msg
        return msg.reply_to_message


class SwapReplySender(AbstractSwap):
    @classmethod
    def get_name(cls):
        return "Swap reply senders"

    def do_swap(self, msg):
        msg.reply_to_message.from_user, msg.from_user = msg.from_user, msg.reply_to_message.from_user
        return msg


class SwapReplyContent(AbstractSwap):
    @classmethod
    def get_name(cls):
        return "Swap reply message content"

    def do_swap(self, msg):
        msg.reply_to_message.text, msg.text = msg.text, msg.reply_to_message.text
        return msg

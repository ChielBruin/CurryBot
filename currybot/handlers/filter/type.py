from currybot.handlers.messageHandler import MessageHandler
from currybot.exceptions import FilterException
from currybot.configResponse import Done, AskChild, NoChild, CreateException


class AbstractIsType(MessageHandler):
    def __init__(self, children):
        super(AbstractIsType, self).__init__(children)

    def check(self, message):
        raise Exception('Not implemented')

    def call(self, bot, message, target, exclude):
        if self.check(message):
            return self.propagate(bot, message, target, exclude)
        else:
            raise FilterException()

    @classmethod
    def is_entrypoint(cls):
        return True

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], AskChild())
        elif stage == 1 and isinstance(arg, MessageHandler):
            data.append(arg)
            return (1, data, AskChild())
        elif stage == 1 and isinstance(arg, NoChild):
            return (-1, None, Done(cls._from_dict({}, data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for abstractIsType')

    def _to_dict(self):
        return {}


class IsReply(AbstractIsType):
    def check(self, message):
        if message.reply_to_message:
            return True
        else:
            return False

    @classmethod
    def get_name(cls):
        return "Message is reply"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsReply(children)


class IsForward(AbstractIsType):
    def check(self, message):
        if message.forward_from:
            return True
        else:
            return False

    @classmethod
    def get_name(cls):
        return "Message is forwarded"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsReply(children)


class Identity(AbstractIsType):
    def check(self, message):
        return True

    @classmethod
    def get_name(cls):
        return "Identity"

    @classmethod
    def _from_dict(cls, dict, children):
        return Identity(children)


class IsPicture(AbstractIsType):
    def check(self, message):
        return message.photo is not None

    @classmethod
    def get_name(cls):
        return "Is picture"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsPicture(children)


class IsVoice(AbstractIsType):
    def check(self, message):
        return message.voice is not None

    @classmethod
    def get_name(cls):
        return "Is voice message"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsVoice(children)


class IsAudio(AbstractIsType):
    def check(self, message):
        return message.audio is not None

    @classmethod
    def get_name(cls):
        return "Is audio"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsAudio(children)


class IsDocument(AbstractIsType):
    def check(self, message):
        return message.document is not None

    @classmethod
    def get_name(cls):
        return "Is document"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsDocument(children)


class IsSticker(AbstractIsType):
    def check(self, message):
        return message.sticker is not None

    @classmethod
    def get_name(cls):
        return "Is sticker"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsSticker(children)


class IsVideo(AbstractIsType):
    def check(self, message):
        return message.video is not None

    @classmethod
    def get_name(cls):
        return "Is video"

    @classmethod
    def _from_dict(cls, dict, children):
        return IsVideo(children)

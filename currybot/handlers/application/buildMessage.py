from currybot.handlers.messageHandler import MessageHandler
from currybot.configResponse import Done, AskChild, NoChild, CreateException, Send


class BuildMessage(MessageHandler):
    def __init__(self, children, message):
        super(BuildMessage, self).__init__(children)
        self.message = message

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
        msg.text = self.apply_message(msg, self.message)
        return self.propagate(bot, msg, target, exclude)

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, Send('Send me the new message text. Valid placeholders:\n%h -> The user handle\n%f -> The first name of the user\n%l The last name of the user\n%n -> The name of the user\n%s -> The original message'))
        elif stage == 1:
            if arg.text:
               return (2, [arg.text, []], AskChild())
            else:
                return (1, data, Send('Please send text and nothing else'))
        elif stage == 2 and isinstance(arg, MessageHandler):
            data[1].append(arg)
            return (2, data, AskChild())
        elif stage == 2 and isinstance(arg, NoChild):
            return (-1, None, Done(BuildMessage(data[1], data[0])))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for buildMessage')

    @classmethod
    def _from_dict(cls, dict, children):
        return BuildMessage(children, dict['message'])

    def _to_dict(self):
        return {'message' : self.message}

    @classmethod
    def get_name(cls):
        return "Set the message text"
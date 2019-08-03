from application.application import Application


class ReplyApplication (Application):
    def __init__(self, id):
        super(ReplyApplication, self).__init__(id)

    def filter(self, msg):
        return msg.reply_to_message


class ParameterizeApplication (Application):
    def __init__(self, id, parameter):
        super(ParameterizeFilter, self).__init__(id)
        self._parameter = parameter

    def filter(self, message):
        message.text = str(self._parameter)
        return message

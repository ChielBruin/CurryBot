from filter.filter import Filter


class IsReplyFilter (Filter):
    def filter(self, message):
        if message.reply_to_message:
            return message
        else:
            return None

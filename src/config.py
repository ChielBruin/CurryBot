class Config (object):
    chat_admins = {}


    @classmethod
    def add_chat_admin(cls, chat_id, admin):
        if chat_id in cls.chat_admins:
            chat_admins = self.chat_admins[chat_id]
            if admin not in chat_admins:
                chat_admins.append(admin)
        else:
            cls.chat_admins[chat_id] = [admin]

    @classmethod
    def is_chat_admin(cls, chat_id, user):
        print(cls.chat_admins)
        print(chat_id, user)
        if chat_id in cls.chat_admins:
            return user in cls.chat_admins[chat_id]
        else:
            Logger.log_error('No admin set for chat %d' % chat_id)
            return False

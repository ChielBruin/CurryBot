from action.action import Action


class StickerAction (Action):
    '''
    An action that sends stickers from given Telegram sticker packs.
    '''

    def __init__(self, id, bot, pack_id, include=None, exclude=None):
        '''
        Configure this action by loading all the stickers from the packs.
        '''
        super(StickerAction, self).__init__(id)
        self.bot = bot

        self.pack_id = pack_id
        self.include = include
        self.exclude = exclude
        self.update()


    def dispatch(self, bot, msg, exclude):
        (id, sticker_id) = self.select_random_option(exclude=exclude)
        bot.send_sticker(chat_id=msg.chat.id, sticker=sticker_id)
        return [id]

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        (id, sticker_id) = self.select_random_option(exclude=exclude)
        bot.send_sticker(chat_id=msg.chat.id, sticker=sticker_id, reply_to_message_id=reply_to)
        return [id]

    def update(self):
        stickerpack = self.bot.get_sticker_set(self.pack_id)
        stickers = list(map(lambda x: x.file_id, stickerpack.stickers))
        self.clear_ids()
        self.append_ids_indexed(stickers, self.include, self.exclude)

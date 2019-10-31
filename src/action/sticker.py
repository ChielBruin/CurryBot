from messageHandler import RandomMessageHandler


class SendSticker (RandomMessageHandler):
    '''
    An action that sends stickers from given Telegram sticker packs.
    '''

    def __init__(self, bot, pack_id, include=None, exclude=None):
        '''
        Configure this action by loading all the stickers from the packs.
        '''
        super(SendSticker, self).__init__(RandomMessageHandler.get_random_id(), [])
        self.bot = bot

        self.pack_id = pack_id
        self.include = include
        self.exclude = exclude
        self.update()

    def call(self, bot, msg, target, exclude):
        (id, sticker_id) = self.select_random_option(exclude=exclude)
        bot.send_sticker(chat_id=msg.chat.id, sticker=sticker_id, reply_to_message_id=target)
        return [id]

    def update(self):
        stickerpack = self.bot.get_sticker_set(self.pack_id)
        stickers = list(map(lambda x: x.file_id, stickerpack.stickers))
        self.clear()
        self.add_options(stickers, self.include, self.exclude)

    def has_effect():
        return True

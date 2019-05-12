from action import Action


class StickerAction (Action):
    '''
    An action that sends stickers from given Telegram sticker packs.
    '''

    def __init__(self, config, bot):
        '''
        Configure this action by loading all the stickers from the packs.
        '''
        super(StickerAction, self).__init__(config)

        for pack in config:
            stickerpack = bot.get_sticker_set(pack['pack'])
            stickers = list(map(lambda x: x.file_id, stickerpack.stickers))

            include = pack['include'] if 'include' in pack else stickers
            exclude = pack['exclude'] if 'exclude' in pack else []

            print('\tLoaded stickerpack \'%s\' containing %d stickers' % (stickerpack.title, len(stickers)))
            n = self.append_ids(stickers, include=include, exclude=exclude)
            print('\t\tSelected %d stickers from the pack' % n)

        print('\t%d stickers loaded' % len(self.ids))

    def trigger(self, bot, message, exclude=[], reply=None):
        chat_id = message.chat_id
        sticker_id = self.select_random_id(exclude=exclude)

        if reply:
            bot.send_sticker(chat_id=chat_id, sticker=sticker_id, reply_to_message_id=reply)
        else:
            bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
        return sticker_id

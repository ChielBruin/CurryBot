from ..messageHandler import RandomMessageHandler
from configResponse import Send, Done, AskChild, AskCacheKey, CreateException


class SendStickerPack (RandomMessageHandler):
    '''
    An action that sends stickers from given Telegram sticker packs.
    '''

    def __init__(self, pack_id):
        '''
        Configure this action by loading all the stickers from the packs.
        '''
        super(SendStickerPack, self).__init__(RandomMessageHandler.get_random_id(), [])
        self.pack_id = pack_id

    def call(self, bot, msg, target, exclude):
        (id, sticker_id) = self.select_random_option(exclude=exclude)
        bot.send_sticker(chat_id=msg.chat.id, sticker=sticker_id, reply_to_message_id=target)
        return [id]

    def on_update(self, bot):
        stickerpack = bot.get_sticker_set(self.pack_id)
        stickers = list(map(lambda x: x.file_id, stickerpack.stickers))
        self.clear()
        self.add_options(stickers)

    def has_effect():
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Send a sticker from a pack"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, Send("Send ma a sticker from the pack"))
        elif stage is 1 and arg:
            if arg.sticker:
                pack = arg.sticker.set_name
                return (-1, None, Done(SendStickerPack(pack)))
            else:
                return (1, None, Send("That is not a sticker, try again"))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendTextMessage')

    def _to_dict(self):
        return {'pack': self.pack_id}

    @classmethod
    def _from_dict(cls, dict, children):
        return SendStickerPack(dict['pack'])

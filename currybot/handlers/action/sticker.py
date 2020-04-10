from currybot.configResponse import Send, Done, CreateException
from currybot.handlers.messageHandler import RandomMessageHandler


class SendStickerPack(RandomMessageHandler):
    """
    An action that sends stickers from given Telegram sticker packs.
    """

    def __init__(self, pack_id):
        """
        Configure this action by loading all the stickers from the packs.
        """
        super(SendStickerPack, self).__init__(RandomMessageHandler.get_random_id(), [])
        self.pack_id = pack_id

    def call(self, bot, message, target, exclude):
        (id, sticker_id) = self.select_random_option(exclude=exclude)
        bot.send_sticker(chat_id=message.chat.id, sticker=sticker_id, reply_to_message_id=target)
        return [id]

    def on_update(self, bot):
        stickerpack = bot.get_sticker_set(self.pack_id)
        stickers = list(map(lambda x: x.file_id, stickerpack.stickers))
        self.clear()
        self.add_options(stickers)

    def has_effect(self):
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
            raise CreateException('Invalid create state for sendStickerPack')

    def _to_dict(self):
        return {'pack': self.pack_id}

    @classmethod
    def _from_dict(cls, dict, children):
        return SendStickerPack(dict['pack'])


class SendStickers(RandomMessageHandler):

    def __init__(self, stickers):
        super(SendStickers, self).__init__(RandomMessageHandler.get_random_id(), [])
        self.add_options(stickers)

    def call(self, bot, msg, target, exclude):
        (id, sticker_id) = self.select_random_option(exclude=exclude)
        bot.send_sticker(chat_id=msg.chat.id, sticker=sticker_id, reply_to_message_id=target)
        return [id]

    def has_effect(self):
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Send a sticker"

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, [], Send("Send ma a sticker to send"))
        elif stage == 1 and arg:
            if arg.sticker:
                data.append(arg.sticker.file_id)
                return (2, data, Send('Do you want to add another sticker?', buttons=Send.YES_NO))
            else:
                return (1, data, Send("That is not a sticker, try again"))
        elif stage == 2:
            if isinstance(arg, str):
                if arg == 'yes':
                    return (1, data, Send("Send ma a new sticker"))
                else:
                    return (-1, None, Done(SendStickers(data)))
            else:
                return (2, data, Send("Clicking a button is hard apparently", buttons=Send.YES_NO))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendStickers')

    def _to_dict(self):
        return {'stickers': self.list_options()}

    @classmethod
    def _from_dict(cls, dict, children):
        return SendStickers(dict['stickers'])

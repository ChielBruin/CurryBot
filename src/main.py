from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import sys, re, random, json

CONFIG   = {}
STICKERS = {}
MESSAGES = {}

def random_sticker(botname, exclude=[]):
    """
    Select a random sticker for the given bot.
    When the sticker is in the excluded list, another one is picked (if possible).
    """
    global STICKERS
    stickers_from = STICKERS[botname]
    if len(stickers_from) is 1:
        return stickers_from[0]

    if len(exclude) is len(stickers_from):
        exclude = []

    while True:
        rand = random.randrange(len(stickers_from))
        sticker = stickers_from[rand]
        if sticker.file_id not in exclude:
             return sticker

def random_message(botname, exclude=[]):
    """
    Select a random message for the given bot.
    When the message is in the excluded list, another one is picked (if possible).
    """
    global MESSAGES
    messages_from = MESSAGES[botname]

    if len(messages_from) is 1:
        return messages_from[0]

    if len(exclude) is len(messages_from):
        exclude = []

    while True:
        rand = random.randrange(len(messages_from))
        message = messages_from[rand]
        if message not in exclude:
             return message

def message_handler(bot, update):
    """
    Check if the received message matches any of the regexes.
    If so, send the stickers
    """
    try:
        global CONFIG
        message = update.message

        for botname in CONFIG:
            if 'messageRegex' in CONFIG[botname]:
                regex = CONFIG[botname]['messageRegex']

                if re.match(regex, message.text):
                    send_reply(botname, bot, message.chat_id, message)
    except Exception as e:
        print(e)

def command_handler(botname, bot, update):
    """
    Reply the stickers when the command of a given bot is called
    """
    try:
        chat_id = update.message.chat_id
        send_reply(botname, bot, chat_id, update.message)
    except Exception as e:
        print(e)

def send_reply(botname, bot, chat_id, message):
    """
    Send a reply to the given message
    If this message is a reply, and transitive replies are enabled,
    Reply to the original message.
    """
    global CONFIG

    reply_to = CONFIG[botname]['replyTo']
    if reply_to == "replies" and not message.reply_to_message:
        return
    elif reply_to == "messages" and message.reply_to_message:
        return

    if CONFIG[botname]['transitiveReply'] and message.reply_to_message:
        msg_id = message.reply_to_message.message_id
    else:
        msg_id = message.message_id

    replies = CONFIG[botname]['replies']
    reply_modes = list(replies.keys())
    reply_mode = reply_modes[random.randrange(len(reply_modes))]

    if reply_mode == 'messages':
        reply_messages(botname, bot, chat_id, message, msg_id)
    else:
        reply_stickers(botname, bot, chat_id, message, msg_id)

def apply_message(message_text, pattern):
    """

    """
    return pattern

def reply_messages(botname, bot, chat_id, message, msg_id):
    """
    Reply messages for the given botname to the message.
    """
    selected = []
    for i in range(CONFIG[botname]['amount']):
        pattern = random_message(botname, exclude=selected)
        selected.append(pattern)
        applied_message = apply_message(message.text, pattern)
        print(applied_message)
        if i > 0:
            bot.send_message(chat_id=chat_id, text=applied_message)
        else:
            bot.send_message(chat_id=chat_id, text=applied_message, reply_to_message_id=msg_id)


def reply_stickers(botname, bot, chat_id, message, msg_id):
    """
    Reply stickers for the given botname to the message.
    """
    global CONFIG

    selected = []
    for i in range(CONFIG[botname]['amount']):
        sticker = random_sticker(botname, exclude=selected)
        selected.append(sticker.file_id)
        print(sticker.emoji)
        if i > 0:
            bot.send_sticker(chat_id=chat_id, sticker=sticker)
        else:
            bot.send_sticker(chat_id=chat_id, sticker=sticker, reply_to_message_id=msg_id)


def init_bot(botname, updater):
    """
    Initialize a bot by getting all the stickers and adding the handlers
    """
    global CONFIG
    global STICKERS, MESSAGES

    dp = updater.dispatcher
    bot = CONFIG[botname]
    amount = bot['amount']

    STICKERS[botname] = []
    MESSAGES[botname] = []

    if not 'amount' in bot:
        print('Ivalid config for %s: \'amount\' not defined' % botname)

    if not 'transitiveReply' in bot:
        print('Ivalid config for %s: \'transitiveReply\' not defined' % botname)

    if not 'replyTo' in bot:
        print('Ivalid config for %s: \'replyTo\' not defined' % botname)

    replies = bot['replies']
    if 'stickers' in replies:
        for pack in replies['stickers']:
            stickerpack = updater.bot.get_sticker_set(pack['pack'])
            include = pack['include'] if 'include' in pack else list(map(lambda x: x.file_id, stickerpack.stickers))
            exclude = pack['exclude'] if 'exclude' in pack else []

            print('\tLoaded stickerpack \'%s\' containing %d stickers' %
                    (stickerpack.title, len(stickerpack.stickers)))

            selected = list(filter(
                lambda x: (x.file_id in include) and (x.file_id not in exclude),
                stickerpack.stickers))
            print('\t\tSelected %d stickers from the pack' % len(selected))
            STICKERS[botname].extend(selected)

        print('\t%d stickers loaded for %s' % (len(STICKERS[botname]), botname))

    if 'messages' in replies:
        MESSAGES[botname].extend(replies['messages'])
        print('\t%d messages loaded for %s' % (len(MESSAGES[botname]), botname))

    if 'commands' in bot:
        print('\tAdding %d command handles' % len(bot['commands']))
        for command in bot['commands']:
            dp.add_handler(CommandHandler(command, (lambda b, u, bot=botname: command_handler(bot, b, u))))

def start_bot(token):
    """
    Start the bot with the given token
    """
    global CONFIG
    updater = Updater(token)

    for bot_config in CONFIG:
        if bot_config == 'api-token':
            continue
        print('Initializing bot %s' % bot_config)
        init_bot(bot_config, updater)

    print('Adding shared message handle')
    updater.dispatcher.add_handler(MessageHandler(Filters.text, message_handler))

    print('\nBot started!\n')
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Please specify the config file')
        exit(1)

    with open(sys.argv[1], "r") as config_file:
        CONFIG = json.load(config_file)

    if 'api-token' in CONFIG:
        start_bot(CONFIG['api-token'])
    elif len(sys.argv) > 2:
        start_bot(sys.argv[2])
    else:
        token = input('What is your token?\n')
        start_bot(token)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters

from logger import Logger
from config import Config
import configResponse

from filter.type     import IsReply, CommandFilter, SenderIsBotAdmin, UserJoinedChat
from filter.composit import Try, Or, PickWeighted, PickUniform, PercentageFilter, Swallow
from filter.regex    import MatchFilter, SearchFilter
from filter.time     import TimeFilter
from action.message  import SendTextMessage, SendMarkdownMessage, SendHTMLMessage
from action.util     import MakeSenderAdmin
from action.sticker  import SendSticker
from action.flickr   import SendFlickr
from application.type import SwapReply, ParameterizeText


class ConfigConversation (object):
    HANDLERS = [
        IsReply, CommandFilter, SenderIsBotAdmin, UserJoinedChat,
        Try, Or, PickWeighted, PickUniform, PercentageFilter, Swallow,
        MatchFilter, SearchFilter,
        TimeFilter,
        SendTextMessage, SendMarkdownMessage, SendHTMLMessage,
        MakeSenderAdmin,
        SendSticker,
        SendFlickr,
        SwapReply, ParameterizeText
    ]

    SELECT_CHAT, SELECT_ACTION, ADD_HANDLER_STEP, ADD_HANDLER_CHILDREN = range(4)
    EXIT, ADD, EDIT, REMOVE, COPY, SKIP = range(6)

    def __init__ (self, bot):
        self.bot = bot

    def start(self, bot, update, user_data):
        user_data['stack'] = []
        user_data['acc'] = []
        user_data['user_msg'] = False
        user = update.message.from_user
        message = update.message
        Logger.log_info("User %s started config conversation." % user.first_name)

        chats = Config.get_admin_chats(message.from_user.id)
        chat_names = [(chat_id, Config.get_chat_title(chat_id)) for chat_id in chats]

        buttons = [[InlineKeyboardButton(text=name, callback_data=str(id))] for (id, name) in chat_names]
        buttons.append([InlineKeyboardButton(text='Exit', callback_data=str(self.EXIT))])
        reply_markup = InlineKeyboardMarkup(buttons)

        # Send message with text and appended InlineKeyboard
        message.reply_text(
            'Select a chat to configure',
            reply_markup=reply_markup
        )
        # Tell ConversationHandler that we're in state `SELECT_ACTION` now
        return self.SELECT_CHAT

    def end(self, bot, update):
        query = update.callback_query
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text='See you next time!',
            reply_markup=None
        )
        return ConversationHandler.END

    def add_initial(self, bot, update, user_data):
        '''
        Add a handler to the current chat
        '''
        if user_data['stack'] == []:
            message = 'Select a filter for the new action'
            handlers = map(lambda x: (x[0], x[1].get_name()), filter(lambda x: x[1].is_entrypoint(), enumerate(self.HANDLERS)))
        else:
            message = 'Select a child handler'
            handlers = map(lambda x: (x[0], x[1].get_name()), enumerate(self.HANDLERS))

        buttons = [
         [InlineKeyboardButton(text=desc, callback_data=str(id))] for (id, desc) in handlers
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        query = update.callback_query
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=message,
            reply_markup=reply_markup
        )
        return self.ADD_HANDLER_STEP

    def add_handler_step(self, bot, msg, user_data, arg=None):
        return self.handle_stack(bot, msg, user_data, arg)

    def handle_stack(self, bot, msg, user_data, arg):
        stack = user_data['stack']
        if len(stack) is 0:
            self.bot.register_message_handler(chat=int(user_data['chat_id']), handler=user_data['acc'][-1])
            self.send_or_edit(bot, user_data, msg, 'Hander added!', None)
            return ConversationHandler.END

        if stack[-1] == 'CHILDREN':
            user_data['stack'] = stack[:-1]
            return self.add_collect_children(bot, msg, user_data)

        (stage, data, idx) = user_data['stack'][-1]
        (stage, data, res) = self.HANDLERS[idx].create(stage, data, arg)
        user_data['stack'][-1] = (stage, data, idx)

        if isinstance(res, configResponse.Send):
            self.send_or_edit(bot, user_data, msg, res.msg, res.buttons)
            return self.ADD_HANDLER_STEP
        elif isinstance(res, configResponse.Done):
            user_data['acc'].append(res.handler)
            user_data['stack'] = user_data['stack'][:-1]
            return self.handle_stack(bot, msg, user_data, None)

        elif isinstance(res, configResponse.AskChildren):
            user_data['acc'].append('CHILDREN')
            user_data['stack'].append('CHILDREN')
            buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton(text='Add a child', callback_data=str(self.ADD)),
                InlineKeyboardButton(text='Pass', callback_data=str(self.SKIP))
            ]])
            self.send_or_edit(bot, user_data, msg, 'Do you want to add a child handler?', buttons)
            return self.ADD_HANDLER_CHILDREN
        else:
            print('Unknown response:', res)
            return ConversationHandler.END

    def add_handler_callback(self, bot, update, user_data):
        query = update.callback_query
        user_data['stack'].append( (0, None, int(query.data)) )
        return self.add_handler_step(bot, query.message, user_data)

    def add_handler_message(self, bot, update, user_data):
        user_data['user_msg'] = True
        return self.add_handler_step(bot, update.message, user_data, arg=update.message)

    def edit_chat(self, bot, update, user_data):
        query = update.callback_query
        chat_id = int(query.data)
        user_data['chat_id'] = chat_id
        chat_name = Config.get_chat_title(chat_id)

        buttons = [[
            InlineKeyboardButton(text='Add a handler', callback_data=str(self.ADD)),
            InlineKeyboardButton(text='Remove handler', callback_data=str(self.REMOVE))
            ],[
            InlineKeyboardButton(text='Edit a handler', callback_data=str(self.EDIT)),
            InlineKeyboardButton(text='Copy a handler', callback_data=str(self.COPY))
            ],[
            InlineKeyboardButton(text='Exit', callback_data=str(self.EXIT))
        ]]

        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text='Select what to configure for chat \'%s\'' % chat_name,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return self.SELECT_ACTION

    def add_collect_children(self, bot, update, user_data):
        children = []
        acc = []
        done = False
        for handler in reversed(user_data['acc']):
            if handler == 'CHILDREN' and not done:
                done = True
            if done:
                acc.append(handler)
            else:
                children.append(handler)
        user_data['acc'] = list(reversed(acc))
        msg = update.callback_query.message if hasattr(update, 'callback_query') else update
        return self.handle_stack(bot, msg, user_data, list(reversed(children)))

    def get_conversation_handler(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('config', self.start, pass_user_data=True)],
            states={
                self.SELECT_CHAT: [
                    CallbackQueryHandler(self.end, pattern='^%s$' % self.EXIT),
                    CallbackQueryHandler(self.edit_chat, pattern='^-?[0-9]{5,}$', pass_user_data=True)
                ],
                self.SELECT_ACTION: [
                    CallbackQueryHandler(self.end, pattern='^%s$' % self.EXIT),
                    CallbackQueryHandler(self.add_initial, pattern='^%s$' % self.ADD, pass_user_data=True),
                    # CallbackQueryHandler(self.edit, pattern='^%s$' % self.EDIT, pass_user_data=True),
                    # CallbackQueryHandler(self.remove, pattern='^%s$' % self.REMOVE, pass_user_data=True),
                    # CallbackQueryHandler(self.copy, pattern='^%s$' % self.COPY, pass_user_data=True)
                ],
                self.ADD_HANDLER_STEP: [
                    CallbackQueryHandler(self.add_handler_callback, pattern='^[0-9]+$', pass_user_data=True),
                    MessageHandler(Filters.all, self.add_handler_message, pass_user_data=True)
                ],
                self.ADD_HANDLER_CHILDREN: [
                    CallbackQueryHandler(self.add_initial, pattern='^%d$' % self.ADD, pass_user_data=True),
                    CallbackQueryHandler(self.add_collect_children, pattern='^%d$' % self.SKIP, pass_user_data=True)
                ]
            },
            fallbacks=[]
        )
        return conv_handler

    def send_or_edit(self, bot, data, original, message, buttons):
        if data['user_msg']:
            bot.send_message(
                chat_id=original.chat_id,
                reply_markup=buttons,
                text=message
            )
        else:
            bot.edit_message_text(
                chat_id=original.chat_id,
                message_id=original.message_id,
                reply_markup=buttons,
                text=message
            )
        data['user_msg'] = False

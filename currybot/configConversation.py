import inspect
import json
import sys
import traceback


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters

from currybot.configResponse import Send, Done, AskChild, NoChild, AskCacheKey, AskAPIKey, CreateException
from currybot.data import Logger, Cache
from currybot.handlerGroup import HandlerGroup
import currybot.handlers


class ConfigConversation(object):
    HANDLERS = [c for (name, c) in inspect.getmembers(sys.modules['currybot.handlers'], inspect.isclass)]
    SELECT_CHAT, SELECT_ACTION, ADD_HANDLER_STEP, ADD_HANDLER_INITIAL, ADD_HANDLER_CHILD, ADD_HANDLER_CACHE_KEY, ADD_HANDLER_API_KEY, REMOVE_HANDLER, COPY_HANDLER, EDIT_HANDLER, EDIT_HANDLER_PARSE = range(11)
    EXIT, ADD, EDIT, REMOVE, COPY, SKIP, TOGGLE = range(7)

    def __init__ (self, bot):
        self.bot = bot

    def start(self, bot, update, user_data):
        if not update.message.chat.type == 'private':
            update.message.reply_text(
                'This command can only be used in a private conversation'
            )
            return ConversationHandler.END

        user_data['stack'] = []
        user_data['acc'] = None
        user_data['user_msg'] = False
        user = update.message.from_user
        message = update.message
        Logger.log_debug("User %s started config conversation." % user.first_name)

        chats = list(Cache.get_admin_chats(message.from_user.id))
        chat_names = [(chat_id, Cache.get_chat_title(chat_id)) for chat_id in chats]

        global_button = [[InlineKeyboardButton(text='Global config', callback_data=HandlerGroup.GLOBAL)]] if str(self.bot.admin_chat) in chats else []
        buttons = [[InlineKeyboardButton(text=name, callback_data=str(id))] for (id, name) in chat_names]
        buttons.append([InlineKeyboardButton(text='Exit', callback_data=str(self.EXIT))])
        reply_markup = InlineKeyboardMarkup(global_button + buttons)

        message.reply_text(
            'Select a chat to configure',
            reply_markup=reply_markup
        )
        return self.SELECT_CHAT

    def end(self, bot, update, user_data):
        msg = update.callback_query.message
        self.send_or_edit(bot, user_data, msg, 'See you next time!')
        return ConversationHandler.END

    def edit_start(self, bot, update, user_data):
        chat_id = user_data['chat_id']
        message_buttons = [[InlineKeyboardButton(text='%s (message)' % name,    callback_data='_0_%d' % idx)] for (idx, (name, _)) in enumerate(self.bot.message_handlers.list(chat_id))]
        tick_buttons    = [[InlineKeyboardButton(text='%s (tick_group)' % name, callback_data='_1_%d' % idx)] for (idx, (name, _)) in enumerate(self.bot.tick_handlers.list(chat_id))]
        button_buttons  = [[InlineKeyboardButton(text='%s (button)' % name,     callback_data='_2_%d' % idx)] for (idx, (name, _)) in enumerate(self.bot.button_handlers.list(chat_id))]
        exit_button     = [[InlineKeyboardButton(text='Exit', callback_data='_3_2')]]
        self.send_or_edit(bot, user_data, update.callback_query.message, 'Select a handler to edit', buttons=message_buttons + tick_buttons + button_buttons + exit_button)
        return self.EDIT_HANDLER

    def edit_send(self, bot, update, user_data):
        if update.callback_query.data[1] == '3':
            self.send_or_edit(bot, user_data, update.callback_query.message, 'Maybe next time')
            return ConversationHandler.END
        try:
            idx = int(update.callback_query.data[3:])
            chat_id = user_data['chat_id']

            if update.callback_query.data[1] == '0':
                handler_group = self.bot.message_handlers
            elif update.callback_query.data[1] == '1':
                handler_group = self.bot.tick_handlers
            else:
                handler_group = self.bot.button_handlers

            name, _ = handler_group.list(chat_id)[idx]
            dict = json.dumps(handler_group.handler_to_dict(chat_id, name))
            user_data['acc'] = (update.callback_query.data[1], chat_id, name)

            self.send_or_edit(bot, user_data, update.callback_query.message, 'Edit this config string and send it back to me:\n%s' % dict)
            return self.EDIT_HANDLER_PARSE
        except:
            traceback.print_exc()

    def edit_end(self, bot, update, user_data):
        user_data['user_msg'] = True
        try:
            dict = json.loads(update.message.text)
            group, chat_id, handler_name = user_data['acc']

            if group == '0':
                handler_group = self.bot.message_handlers
            elif group == '1':
                handler_group = self.bot.tick_handlers
            else:
                handler_group = self.bot.button_handlers

            handler_group.update_handler_from_dict(chat_id, handler_name, dict)
            self.send_or_edit(bot, user_data, update.message, 'Handler updated')
            return ConversationHandler.END
        except json.JSONDecodeError:
            self.send_or_edit(bot, user_data, update.message, 'Invalid string, it must be valid JSON')
            return self.EDIT_HANDLER_PARSE
        except:
            self.send_or_edit(bot, user_data, update.message, 'Invalid input, it must be a valid config')
            return self.EDIT_HANDLER_PARSE

    def copy_start(self, bot, update, user_data):
        msg = update.callback_query.message
        chats = Cache.get_admin_chats(update._effective_user.id)
        chat_names = [(chat_id, Cache.get_chat_title(chat_id)) for chat_id in chats if not chat_id == user_data['chat_id']]
        if chat_names:
            global_button = [[InlineKeyboardButton(text='Global config', callback_data=HandlerGroup.GLOBAL)]] if str(self.bot.admin_chat) in chats else []
            buttons = [[InlineKeyboardButton(text=name, callback_data=str(id))] for (id, name) in chat_names]
            message = 'Select a chat to copy a handler from'
            self.send_or_edit(bot, user_data, msg, message, global_button + buttons)
            return self.COPY_HANDLER
        else:
            self.send_or_edit(bot, user_data, msg, 'No chats to copy from')
            return ConversationHandler.END

    def copy_select_handler(self, bot, update, user_data):
        chat_id = update.callback_query.data
        user_data['acc'] = chat_id

        msg_handlers = [(idx, name) for (idx, (name, handler)) in enumerate(self.bot.message_handlers.list(chat_id)) if not handler.is_private()]
        msg_buttons = [InlineKeyboardButton(text='%s (message)' % name, callback_data='_0_%d' % idx) for (idx, name) in msg_handlers]
        tick_handlers = [(idx, name) for (idx, (name, handler)) in enumerate(self.bot.tick_handlers.list(chat_id)) if not handler.is_private()]
        tick_buttons = [InlineKeyboardButton(text='%s (tick)' % name, callback_data='_1_%d' % idx) for (idx, name) in tick_handlers]
        button_handlers = [(idx, name) for (idx, (name, handler)) in enumerate(self.bot.button_handlers.list(chat_id)) if not handler.is_private()]
        button_buttons = [InlineKeyboardButton(text='%s (button)' % name, callback_data='_2_%d' % idx) for (idx, name) in tick_handlers]

        buttons = [[button] for button in msg_buttons + tick_buttons + button_buttons]
        if buttons:
            message = 'Select a handler to copy'
            self.send_or_edit(bot, user_data, update.callback_query.message, message, buttons)
            return self.COPY_HANDLER
        else:
            self.send_or_edit(bot, user_data, update.callback_query.message, 'No handlers to copy from this chat')
            return ConversationHandler.END

    def copy_handler(self, bot, update, user_data):
        try:
            type = int(update.callback_query.data[1])
            if type == 0:
                handler_group = self.bot.message_handlers
            elif type == 1:
                handler_group = self.bot.tick_handlers
            elif type == 2:
                handler_group = self.bot.button_handlers
            else:
                raise Exception('Unknown handler type %d' % type)

            idx = int(update.callback_query.data[3:])
            chat_id = user_data['acc']
            (name, handler) = handler_group.list(chat_id)[idx]
            handler_group.register(chat=user_data['chat_id'], name=name, handler=handler)

            self.send_or_edit(bot, user_data, update.callback_query.message, 'Copied \'%s\'' % name)
            return ConversationHandler.END
        except:
            traceback.print_exc()

    def remove_start(self, bot, update, user_data):
        chat_id = user_data['chat_id']
        message_buttons = [[InlineKeyboardButton(text='%s (message)' % name,    callback_data='_0_%d' % idx)] for (idx, (name, _)) in enumerate(self.bot.message_handlers.list(chat_id))]
        tick_buttons    = [[InlineKeyboardButton(text='%s (tick_group)' % name, callback_data='_1_%d' % idx)] for (idx, (name, _)) in enumerate(self.bot.tick_handlers.list(chat_id))]
        button_buttons  = [[InlineKeyboardButton(text='%s (button)' % name,     callback_data='_2_%d' % idx)] for (idx, (name, _)) in enumerate(self.bot.button_handlers.list(chat_id))]
        exit_button     = [[InlineKeyboardButton(text='Exit', callback_data='_3_2')]]
        self.send_or_edit(bot, user_data, update.callback_query.message, 'Select a handler to remove', buttons=message_buttons + tick_buttons + button_buttons + exit_button)
        return self.REMOVE_HANDLER

    def remove_end(self, bot, update, user_data):
        if update.callback_query.data[1] == '3':
            self.send_or_edit(bot, user_data, update.callback_query.message, 'Maybe next time')
            return ConversationHandler.END
        try:
            idx = int(update.callback_query.data[3:])
            chat_id = user_data['chat_id']

            if update.callback_query.data[1] == '0':
                handler_group = self.bot.message_handlers
            elif update.callback_query.data[1] == '1':
                handler_group = self.bot.tick_handlers
            else:
                handler_group = self.bot.button_handlers

            name, _ = handler_group.list(chat_id)[idx]
            handler_group.remove(chat_id, name)

            Logger.log_info('Removed \'%s\'' % name)
            self.send_or_edit(bot, user_data, update.callback_query.message, 'Removed \'%s\'' % name)
            return ConversationHandler.END
        except:
            traceback.print_exc()

    def add_start(self, bot, update, user_data):
        buttons = [[
         InlineKeyboardButton(text='Every minute', callback_data='0'),
         InlineKeyboardButton(text='Every message', callback_data='1'),
         InlineKeyboardButton(text='Button press', callback_data='2')
        ]]
        self.send_or_edit(bot, user_data, update.callback_query.message, 'Should the rule trigger on receiving a message, every minute or when a button is pressed?', buttons=buttons)
        return self.ADD_HANDLER_INITIAL

    def add_initial_type_msg(self, bot, update, user_data):
        message = update.callback_query.message
        user_data['type'] = 'msg'
        return self._add_initial_type(bot, message, user_data)

    def add_initial_type_tick(self, bot, update, user_data):
        message = update.callback_query.message
        user_data['type'] = 'tick'
        return self._add_initial_type(bot, message, user_data)

    def add_initial_type_button(self, bot, update, user_data):
        message = update.callback_query.message
        user_data['type'] = 'button'
        return self._add_initial_type(bot, message, user_data)

    def _add_initial_type(self, bot, message, data):
        self.send_or_edit(bot, data, message, 'Please send me a name for the new handler')
        return self.ADD_HANDLER_INITIAL

    def add_initial(self, bot, update, user_data):
        """
        Add a handler to the current chat
        """
        user_data['user_msg'] = True
        if update.message.text:
            name = update.message.text
            if not self.bot.has_handler_with_name(user_data['chat_id'], name):
                user_data['name'] = name
                message = 'Select a filter for \'%s\'' % name
                handlers = map(lambda x: (x[0], x[1].get_name()), filter(lambda x: x[1].is_entrypoint(), enumerate(self.HANDLERS)))

                buttons = [
                 [InlineKeyboardButton(text=desc, callback_data=str(id))] for (id, desc) in handlers
                ]

                self.send_or_edit(bot, user_data, update.message, message, buttons)
                return self.ADD_HANDLER_STEP
            else:
                self.send_or_edit(bot, user_data, update.message, "Name already in use. Please send an other one")
                return self.ADD_HANDLER_INITIAL
        else:
            message = 'Invalid name. It must contain text'
            self.send_or_edit(bot, user_data, update.message, message)
            return self.ADD_HANDLER_INITIAL

    def handle_stack(self, bot, msg, user_data):
        stack = user_data['stack']
        if stack:
            handler = user_data['acc']
            chat_id = user_data['chat_id']
            name = user_data['name']
            type = user_data['type']
            if type == 'tick':
                self.bot.tick_handlers.register(chat=chat_id, handler=handler, name=name)
                Logger.log_info('Added tick handler \'%s\'' % name)
            elif type == 'msg':
                self.bot.message_handlers.register(chat=chat_id, name=name, handler=handler)
                Logger.log_info('Added message handler \'%s\'' % name)
            elif type == 'button':
                self.bot.button_handlers.register(chat=chat_id, name=name, handler=handler)
                Logger.log_info('Added button handler \'%s\'' % name)
            else:
                message = 'Unknown handler type %s' % type
                Logger.log_error(message)
                self.send_or_edit(bot, user_data, msg, message)
                return ConversationHandler.END
            self.send_or_edit(bot, user_data, msg, 'Hander added!')
            return ConversationHandler.END

        (stage, data, idx) = stack[-1]
        try:
            current = self.HANDLERS[idx]
            (stage, data, res) = current.create(stage, data, user_data['acc'])
            stack[-1] = (stage, data, idx)
            user_data['acc'] = None

            if isinstance(res, Send):
                self.send_or_edit(bot, user_data, msg, res.msg, res.buttons)
                return self.ADD_HANDLER_STEP

            elif isinstance(res, Done):
                user_data['acc'] = res.handler
                user_data['stack'] = user_data['stack'][:-1]
                return self.handle_stack(bot, msg, user_data)

            elif isinstance(res, AskChild):
                name = current.get_name()
                message = 'Do you want to add a child handler for \'%s\'' % name
                buttons = [[
                    InlineKeyboardButton(text='yes', callback_data='-2'),
                    InlineKeyboardButton(text='no', callback_data='-1')
                ]]

                self.send_or_edit(bot, user_data, msg, message, buttons)
                return self.ADD_HANDLER_CHILD

            elif isinstance(res, AskCacheKey):
                user_data['acc'] = res.default
                buttons = [
                    [InlineKeyboardButton(text='Create own key', callback_data=str(self.ADD))],
                    [InlineKeyboardButton(text='Use existing key', callback_data=str(self.COPY))]
                ]

                self.send_or_edit(bot, user_data, msg, 'Select a cache key, or create a new one', buttons)
                return self.ADD_HANDLER_CACHE_KEY

            elif isinstance(res, AskAPIKey):
                stack = user_data['stack']
                stack.append( (0, None, stack[-1][2]) )
                buttons = [
                    [InlineKeyboardButton(text='Create own API key', callback_data=str(self.ADD))],
                    [InlineKeyboardButton(text='Use existing API key', callback_data=str(self.COPY))]
                ]

                self.send_or_edit(bot, user_data, msg, 'Select an API key, or create a new one', buttons)
                return self.ADD_HANDLER_API_KEY
            else:
                raise Exception('Unknown response: %s' % res)
        except CreateException as ex:
            traceback.print_exc()
            self.send_or_edit(bot, user_data, msg, 'Implementation missing! Please report your steps to the developer')
            return ConversationHandler.END
        except Exception as ex:
            traceback.print_exc()
            self.send_or_edit(bot, user_data, msg, 'Error while processing handler create event! Please report your steps to the developer')
            return ConversationHandler.END

    def add_handler_callback(self, bot, update, user_data):
        query = update.callback_query
        data = {'user_id': query.from_user.id, 'chat_id': user_data['chat_id']}
        user_data['stack'].append( (0, data, int(query.data)) )
        return self.handle_stack(bot, query.message, user_data)

    def add_handler_button_callback(self, bot, update, user_data):
        query = update.callback_query
        user_data['acc'] = query.data
        return self.handle_stack(bot, query.message, user_data)

    def add_handler_message(self, bot, update, user_data):
        user_data['user_msg'] = True
        user_data['acc'] = update.message
        return self.handle_stack(bot, update.message, user_data)

    def add_handler_no_child_callback(self, bot, update, user_data):
        user_data['acc'] = NoChild()
        return self.handle_stack(bot, update.callback_query.message, user_data)

    def add_handler_select_child_callback(self, bot, update, user_data):
        stack = user_data['stack']
        current_idx = stack[-1][2]
        message = 'Select a handler for %s' % self.HANDLERS[current_idx].get_name()
        handlers = map(lambda x: (x[0], x[1].get_name()), filter(lambda x: not x[0] is current_idx, enumerate(self.HANDLERS)))

        buttons = [
         [InlineKeyboardButton(text=desc, callback_data=str(id))] for (id, desc) in handlers
        ]

        self.send_or_edit(bot, user_data, update.callback_query.message, message, buttons)
        return self.ADD_HANDLER_CHILD

    def add_handler_select_cache_key_callback(self, bot, update, user_data):
        stack = user_data['stack']
        current_idx = stack[-1][2]
        user_id = update.callback_query.from_user.id

        keys = [key for chat_id in Cache.get_admin_chats(user_id) for key in Cache.get_chat_keys(chat_id)]
        if keys:
            message = 'You do not have access to any existing keys, please send me a valid key'
            buttons = None
        else:
            message = 'Select a key'
            buttons = [[InlineKeyboardButton(text=key, callback_data='0_' + str(key))] for key in keys]

        self.send_or_edit(bot, user_data, update.callback_query.message, message, buttons)
        return self.ADD_HANDLER_CACHE_KEY

    def add_handler_new_cache_key_callback(self, bot, update, user_data):
        message = 'Please send me a cache key to use (max length is 32)'
        self.send_or_edit(bot, user_data, update.callback_query.message, message)
        return self.ADD_HANDLER_CACHE_KEY

    def add_handler_cache_key_msg(self, bot, update, user_data):
        user_data['user_msg'] = True
        if update.message.text:
            key = update.message.text.strip()
            if Cache.contains(key) or len(key) >= 32 or key.startswith('$'):
                message = 'Invalid key. Either it is already in use, starts with a $, or it is too long'
                self.send_or_edit(bot, user_data, update.message, message)
                return self.ADD_HANDLER_CACHE_KEY
            else:
                default = user_data['acc']
                user_data['acc'] = key
                Cache.config_entry(key, True)
                if not Cache.contains(key):
                    Cache.put(key, default)
                Cache.add_chat_key(key, user_data['chat_id'])
                return self.handle_stack(bot, update.message, user_data)
        else:
            message = 'Invalid key. It must contain text'
            self.send_or_edit(bot, user_data, update.message, message)
            return self.ADD_HANDLER_CACHE_KEY

    def add_handler_key_callback(self, bot, update, user_data):
        query = update.callback_query
        user_data['acc'] = query.data[2:]
        return self.handle_stack(bot, query.message, user_data)

    def add_handler_select_api_key_callback(self, bot, update, user_data):
        try:
            user_id = update.callback_query.from_user.id

            chat_id = user_data['chat_id']
            keys = [key for key in Cache.get_api_keys(chat_id)]

            if keys:
                message = 'You do not have access to any existing API keys, please send me a valid key name'
                buttons = None

            else:
                message = 'Select an API key'
                buttons = [[InlineKeyboardButton(text=key, callback_data='0_' + str(key))] for key in keys]
                user_data['stack'] = user_data['stack'][:-1]
            self.send_or_edit(bot, user_data, update.callback_query.message, message, buttons)
            return self.ADD_HANDLER_API_KEY
        except Exception:
            traceback.print_exc()

    def add_handler_new_api_key_callback(self, bot, update, user_data):
        message = 'Please send me a name for your API key (max length is 32)'
        self.send_or_edit(bot, user_data, update.callback_query.message, message)
        return self.ADD_HANDLER_API_KEY

    def add_handler_api_key_msg(self, bot, update, user_data):
        user_data['user_msg'] = True
        try:
            if update.message.text:
                val = update.message.text.strip()

                (stage, data, idx) = user_data['stack'][-1]
                if stage == 0 and (Cache.contains(val) or len(val) >= 32 or val.startswith('$')):
                    message = 'Invalid API key name. Either it is already in use, it starts with a $, or it is too long'
                    self.send_or_edit(bot, user_data, update.message, message)
                else:
                    (stage, data, res) = self.HANDLERS[idx].create_api(stage, data, val)
                    user_data['stack'][-1] = (stage, data, idx)

                    if isinstance(res, Send):
                        self.send_or_edit(bot, user_data, update.message, res.msg, res.buttons)
                        return self.ADD_HANDLER_API_KEY
                    elif isinstance(res, Done):
                        (key, value) = res.handler
                        user_data['acc'] = key
                        Cache.config_entry(key, True)
                        Cache.add_api_key(key, user_data['chat_id'])
                        Cache.put(key, value, encrypt=True)

                        user_data['stack'] = user_data['stack'][:-1]
                        return self.handle_stack(bot, update.message, user_data)
                    else:
                        print(stage, data, res)
                        self.send_or_edit(bot, user_data, update.message, 'Unexpected API creation state! Please report your steps to the developer')
                        return ConversationHandler.END
            else:
                message = 'Invalid reply. It must contain text'
                self.send_or_edit(bot, user_data, update.message, message)
                return self.ADD_HANDLER_API_KEY
        except Exception:
            traceback.print_exc()

    def toggle_standalone(self, bot, update, user_data):
        chat_id = user_data['chat_id']
        new_state = not Cache.chat_is_standalone(chat_id)
        Cache.chat_set_standalone(chat_id, new_state)
        self.send_or_edit(bot, user_data, update.callback_query.message, '%s global handlers' % ('Disabled' if new_state else 'Enabled'))
        return ConversationHandler.END

    def edit_chat(self, bot, update, user_data):
        query = update.callback_query
        chat_id = query.data
        user_data['chat_id'] = chat_id
        chat_name = 'global handlers' if chat_id == HandlerGroup.GLOBAL else Cache.get_chat_title(chat_id)

        toggle_global_text = '%s global handlers' %('Enable' if Cache.chat_is_standalone(chat_id) else 'Disable')

        buttons = [[
            InlineKeyboardButton(text='Add a handler', callback_data=str(self.ADD)),
            InlineKeyboardButton(text='Remove handler', callback_data=str(self.REMOVE))
            ], [
            InlineKeyboardButton(text='Edit a handler', callback_data=str(self.EDIT)),
            InlineKeyboardButton(text='Copy a handler', callback_data=str(self.COPY))
        ]]
        toggle_button = [[InlineKeyboardButton(text=toggle_global_text, callback_data=str(self.TOGGLE))]] if chat_id != HandlerGroup.GLOBAL else []
        exit_button   = [[InlineKeyboardButton(text='Exit', callback_data=str(self.EXIT))]]

        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text='Select what to configure for chat \'%s\'' % chat_name,
            reply_markup=InlineKeyboardMarkup(buttons + toggle_button + exit_button)
        )
        return self.SELECT_ACTION

    def get_conversation_handler(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('config', self.start, pass_user_data=True)],
            states={
                self.SELECT_CHAT: [
                    CallbackQueryHandler(self.end, pattern='^%s$' % self.EXIT, pass_user_data=True),
                    CallbackQueryHandler(self.edit_chat, pattern='^(%s)|(-?[0-9]{5,})$' % HandlerGroup.GLOBAL, pass_user_data=True)
                ],
                self.SELECT_ACTION: [
                    CallbackQueryHandler(self.end, pattern='^%s$' % self.EXIT, pass_user_data=True),
                    CallbackQueryHandler(self.add_start, pattern='^%s$' % self.ADD, pass_user_data=True),
                    CallbackQueryHandler(self.edit_start, pattern='^%s$' % self.EDIT, pass_user_data=True),
                    CallbackQueryHandler(self.remove_start, pattern='^%s$' % self.REMOVE, pass_user_data=True),
                    CallbackQueryHandler(self.copy_start, pattern='^%s$' % self.COPY, pass_user_data=True),
                    CallbackQueryHandler(self.toggle_standalone, pattern='^%s$' % self.TOGGLE, pass_user_data=True)
                ],
                self.COPY_HANDLER: [
                    CallbackQueryHandler(self.copy_select_handler, pattern='^-?[\d]+$', pass_user_data=True),
                    CallbackQueryHandler(self.copy_handler, pattern='^_[012]_[\d]+$', pass_user_data=True),
                ],
                self.REMOVE_HANDLER: [
                    CallbackQueryHandler(self.remove_end, pattern='^_[0123]_-?[\d]+$', pass_user_data=True)
                ],
                self.ADD_HANDLER_INITIAL: [
                    CallbackQueryHandler(self.add_initial_type_tick, pattern='^0$', pass_user_data=True),
                    CallbackQueryHandler(self.add_initial_type_msg, pattern='^1$', pass_user_data=True),
                    CallbackQueryHandler(self.add_initial_type_button, pattern='^2$', pass_user_data=True),
                    MessageHandler(Filters.all, self.add_initial, pass_user_data=True)
                ],
                self.ADD_HANDLER_STEP: [
                    CallbackQueryHandler(self.add_handler_callback, pattern='^[0-9]+$', pass_user_data=True),
                    CallbackQueryHandler(self.add_handler_button_callback, pattern='^[a-zA-Z].*$', pass_user_data=True),
                    MessageHandler(Filters.all, self.add_handler_message, pass_user_data=True)
                ],
                self.ADD_HANDLER_CHILD: [
                    CallbackQueryHandler(self.add_handler_no_child_callback, pattern='^-1$', pass_user_data=True),
                    CallbackQueryHandler(self.add_handler_select_child_callback, pattern='^-2$', pass_user_data=True),
                    CallbackQueryHandler(self.add_handler_callback, pattern='^[0-9]+$', pass_user_data=True)
                ],
                self.ADD_HANDLER_CACHE_KEY: [
                    CallbackQueryHandler(self.add_handler_key_callback, pattern='^0_.+$', pass_user_data=True),
                    CallbackQueryHandler(self.add_handler_new_cache_key_callback, pattern='^%s$' % self.ADD, pass_user_data=True),
                    CallbackQueryHandler(self.add_handler_select_cache_key_callback, pattern='^%s$' % self.COPY, pass_user_data=True),
                    MessageHandler(Filters.all, self.add_handler_cache_key_msg, pass_user_data=True)
                ],
                self.ADD_HANDLER_API_KEY: [
                    CallbackQueryHandler(self.add_handler_key_callback, pattern='^0_.+$', pass_user_data=True),
                    CallbackQueryHandler(self.add_handler_new_api_key_callback, pattern='^%s$' % self.ADD, pass_user_data=True),
                    CallbackQueryHandler(self.add_handler_select_api_key_callback, pattern='^%s$' % self.COPY, pass_user_data=True),
                    MessageHandler(Filters.all, self.add_handler_api_key_msg, pass_user_data=True)
                ],
                self.EDIT_HANDLER: [
                    CallbackQueryHandler(self.edit_send, pattern='^_[0123]_-?[\d]+$', pass_user_data=True)
                ],
                self.EDIT_HANDLER_PARSE: [
                    MessageHandler(Filters.all, self.edit_end, pass_user_data=True)
                ]
            },
            fallbacks=[]
        )
        return conv_handler

    def send_or_edit(self, bot, data, original, message, buttons=None):
        buttons = None if buttons is None else InlineKeyboardMarkup(buttons)
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

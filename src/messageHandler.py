from telegram.ext import CommandHandler, Filters
from telegram import Message, Chat

import re, random
from datetime import datetime, timedelta

from replyBehaviour import ReplyBehaviour
from timedTrigger import TimedTrigger

from stickerAction import StickerAction
from flickrAction  import FlickrAction
from messageAction import MessageAction
from forwardAction import ForwardAction
from rssAction     import RSSAction

from ytPlaylistAppend import YtPlaylistAppend


class CurryBotMessageHandler (object):
    '''
    Handler for an action group.
    Handles random selection of actions (ensuring no repetitions).
    '''

    def __init__(self, bot, config):
        self.bot = bot
        self.update(config)

    def update (self, config):
        '''
        Update this handler using the given config.
        Registers the correct actions and commands.
        '''
        self.amount = int(config['amount'])
        self.replyBehaviour = ReplyBehaviour(config['replyBehaviour'])
        self.actions = []

        if 'chats' in config:
            chats = config['chats']
            self.groups_include = chats['include'] if 'include' in chats else None
            self.groups_exclude = chats['exclude'] if 'exclude' in chats else []
        else:
            self.groups_include = None
            self.groups_exclude = []

        if 'accuracy' in config:
            acc = config['accuracy']
            if isinstance(acc, str):
                acc = float(acc[:-1]) / 100      # Convert percentage

            self.accuracy = max(0, min(1, acc))
        else:
            self.accuracy = 1

        self.update_triggers(config)
        self.update_side_effects(config)
        self.update_actions(config)

    def update_side_effects(self, config):
        '''
        Update the configs for the side effects.
        '''
        self.side_effects = []
        if 'side-effects' in config:
            effects = config['side-effects']
            if 'ytPlaylistAppend' in effects:
                self.side_effects.append(YtPlaylistAppend(effects['ytPlaylistAppend'], self.bot.get_api_key('youtube')))

    def update_triggers(self, config):
        '''
        Update the trigger configs.
        '''
        self.triggers = {}
        if 'triggers' not in config or config['triggers'] is {}:
            raise Exception('Malformed config, \'triggers\' could not be found')

        triggers = config['triggers']
        if 'commands' in triggers:
            for command in triggers['commands']:
                self.bot.dispatcher.add_handler(CommandHandler(command,
                                                (lambda bot, update, self=self: self.on_receive_command(bot, update))))
        if 'when_time' in triggers:
            if 'chats' in config and 'include' in config['chats']:
                for time_filter in triggers['when_time']:
                    TimedTrigger(self.bot.dispatcher.job_queue,
                                 when=time_filter,
                                 groups=config['chats']['include'],
                                 handler=self)
            else:
                print('\'when_time\' requires whitelisted groups')

        if 'inactive_time' in triggers:
            if 'chats' in config and 'include' in config['chats']:
                time = triggers['inactive_time']
                if 'h' in time or 'H' in time:
                    delta = timedelta(hours=int(time[:-1]))
                elif 'm' in time or 'M' in time:
                    delta = timedelta(minutes=int(time[:-1]))
                else:
                    delta = timedelta(minutes=int(time))
                self.add_trigger('tick',
                                    lambda bot, chats, self=self: self.on_inactive_update(bot, chats, delta))
            else:
                print('\'inactive_time\' requires whitelisted groups')

        if 'message' in triggers:
            self.add_trigger('text',
                                lambda b, u: self.on_receive_message(b, u, triggers['message']))

        if 'url' in triggers:
            self.add_trigger('text',
                                lambda b, u: self.on_receive_message(b, u, map(lambda x: r'.*%s' % x, triggers['url'])))

        if 'audio' in triggers and triggers['audio']:
            self.add_trigger('audio', lambda b, u: self.on_trigger(b, u.message))

        if 'video' in triggers and triggers['video']:
            self.add_trigger('video', lambda b, u: self.on_trigger(b, u.message))

        if 'image' in triggers and triggers['image']:
            self.add_trigger('image', lambda b, u: self.on_trigger(b, u.message))

        if 'contact' in triggers and triggers['contact']:
            self.add_trigger('contact', lambda b, u: self.on_trigger(b, u.message))

        if 'document' in triggers and triggers['document']:
            self.add_trigger('document', lambda b, u: self.on_trigger(b, u.message))

        if 'sticker' in triggers and triggers['sticker']:
            self.add_trigger('sticker', lambda b, u: self.on_trigger(b, u.message))

        if 'voice' in triggers and triggers['voice']:
            self.add_trigger('voice', lambda b, u: self.on_trigger(b, u.message))

    def on_inactive_update(self, bot, chats, time_delta):
        '''
        Callback for the `tick` action.
        If chats have been inactive for too long, triggers a reply action.
        '''
        for chat_id in self.groups_include:
            if chat_id in chats and time_delta < chats[chat_id]:
                    now = datetime.now()
                    self.on_receive_anonymous(bot, chat_id, now)
                    self.bot.active_timers[str(chat_id)] = now - timedelta(seconds=2)

    def update_actions(self, config):
        '''
        Update the settings for the action handlers.
        '''
        replies = config['replies']
        triggers = config['triggers']
        for action in replies:
            if action == 'messages':
                self.actions.append(MessageAction(replies[action], triggers['message'] if 'message' in triggers else []))
            elif action == 'stickers':
                self.actions.append(StickerAction(replies[action], self.bot.updater.bot))
            elif action == 'flickr_images':
                self.actions.append(FlickrAction(replies[action], self.bot.get_api_key('flickr')))
            elif action == 'forward':
                self.actions.append(ForwardAction(replies[action]))
            elif action == 'rss':
                self.actions.append(RSSAction(replies[action]))
            else:
                print('Unrecognized reply type \'%s\'' % action)

    def add_trigger(self, type, handler):
        '''
        Add a trigger of the given type to the list of triggers.
        '''
        if type in self.triggers:
            self.triggers[type].append(handler)
        else:
            self.triggers[type] = [handler]

    def on_receive_anonymous(self, bot, chat_id, datetime, msg_text=''):
        '''
        Calls trigger with a dummy message.
        '''
        msg = Message(-1, None, datetime, Chat(chat_id, 'Dummy'), text=msg_text)
        self.on_trigger(bot, msg)

    def on_receive_message(self, bot, update, regexes):
        '''
        Called when a message is received by the bot.
        When this message matches this handler, trigger the actions.
        '''
        message = update.message
        for regex in regexes:
            if re.match(regex, message.text):
                self.on_trigger(bot, message)
                return

    def on_receive_command(self, bot, update):
        '''
        Called when a command is received by the bot.
        This will trigger the actions.
        '''
        try:
            self.on_trigger(bot, update.message)
        except Exception as e:
            print('Error in \'on_receive_command\':')
            print(e)

    def select_action(self):
        '''
        Select a random action, keeping in mind their weight.
        THis ensures fair and configurable selection of actions.
        '''
        size = sum(map(lambda x: len(x), self.actions))
        rand = random.randrange(size)

        weight = 0
        for action in self.actions:
            weight += len(action)
            if weight >= rand:
                return action
            else:
                continue

    def on_trigger(self, bot, message):
        '''
        Called when this handler is triggered.
        Triggers the actions with the correct parameters.
        '''
        # If current chat is excluded, skip the trigger
        chat_id = str(message.chat.id)
        if (self.groups_include and (chat_id not in self.groups_include)) or (chat_id in self.groups_exclude):
            return

        if self.accuracy < random.random():
            return

        try:
            for effect in self.side_effects:
                effect.trigger(message)
        except Exception as e:
            print('An exception occured in one of the side effect handlers')
            print(e)

        exclude = []
        for i in range(self.amount):
            action = self.select_action()
            try:
                target = self.replyBehaviour.select_target(message, i)
                exclude.append(action.trigger(bot, message, exclude=exclude, reply=target))
            except IndexError:
                pass

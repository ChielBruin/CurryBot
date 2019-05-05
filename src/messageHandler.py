from telegram.ext import CommandHandler, Filters
import re, random

from replyBehaviour import ReplyBehaviour

from stickerAction import StickerAction
from flickrAction  import FlickrAction
from messageAction import MessageAction
from forwardAction import ForwardAction


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

        if 'messageRegex' in config:
            self.regex = str(config['messageRegex'])
        else:
            self.regex = None

        if 'accuracy' in config:
            acc = config['accuracy']
            if isinstance(acc, str):
                acc = float(acc[:-1]) / 100      # Convert percentage

            self.accuracy = max(0, min(1, acc))
        else:
            self.accuracy = 1

        if 'commands' in config:
            for command in config['commands']:
                self.bot.dispatcher.add_handler(CommandHandler(command,
                                               (lambda bot, update, self=self: self.on_receive_command(bot, update))))

        replies = config['replies']
        for action in replies:
            if action == 'messages':
                self.actions.append(MessageAction(replies[action], self.regex))
            elif action == 'stickers':
                self.actions.append(StickerAction(replies[action], self.bot.updater.bot))
            elif action == 'flickr_images':
                self.actions.append(FlickrAction(replies[action], self.bot.get_api_key('flickr')))
            elif action == 'forward':
                self.actions.append(ForwardAction(replies[action]))
            else:
                print('Unrecognized reply type \'%s\'' % action)


    def on_receive_message(self, bot, update):
        '''
        Called when a message is received by the bot.
        When this message matches this handler, trigger the actions.
        '''
        try:
            message = update.message
            if re.match(self.regex, message.text):
                self.on_trigger(bot, message)
        except Exception as e:
            print('Error in \'on_receive_message\':')
            print(e)

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

        exclude = []
        for i in range(self.amount):
            action = self.select_action()
            try:
                target = self.replyBehaviour.select_target(message, i)
                exclude.append(action.trigger(bot, message, exclude=exclude, reply=target))
            except IndexError:
                pass

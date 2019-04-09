from telegram.ext import CommandHandler, Filters
import re, random

from stickerAction import StickerAction
from flickrAction  import FlickrAction
from messageAction import MessageAction


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
        self.amount = config['amount']
        self.transitiveReply = config['transitiveReply']
        self.reply_to = config['replyTo']
        self.actions = []

        if 'messageRegex' in config:
            self.regex = config['messageRegex']
        else:
            self.regex = None

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
        if self.reply_to == "replies" and not message.reply_to_message:
            return
        elif self.reply_to == "messages" and message.reply_to_message:
            return

        target = message.message_id
        if self.transitiveReply and message.reply_to_message:
            target = message.reply_to_message.message_id

        exclude = []
        for i in range(self.amount):
            action = self.select_action()
            exclude.append(action.trigger(bot, message, exclude=exclude, reply=target if i is 0 else None))

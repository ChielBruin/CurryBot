import re
import requests

from currybot.configResponse import Send, Done, AskAPIKey, CreateException
from currybot.data.cache import Cache
from currybot.data.logger import Logger
from currybot.handlers.messageHandler import RandomMessageHandler


class SendFlickr (RandomMessageHandler):
    '''
    An action that sends images from Flickr albums when triggered.
    '''

    def __init__(self, id, api_key, pack):
        '''
        Initialize a FlickrAction by preloading the images in the given albums.
        '''
        super(SendFlickr, self).__init__(id, [], do_cache=True)
        self.key = api_key
        self.pack = pack

    def on_update(self, bot):
        Logger.log_debug('Updating flickr cache')
        flickr_album = self.make_request('flickr.photosets.getPhotos', 'photoset', {'photoset_id': self.pack})
        name = flickr_album['title']
        images = list(map(lambda x: x['id'], flickr_album['photo']))

        self.add_options(images, (lambda id, self=self: self.load_image(id)))

    def load_image(self, id):
        '''
        Load an image from the given id.
        '''
        Logger.log_debug('Requesting image with id %s' % id)
        try:
            photo = self.make_request('flickr.photos.getInfo', 'photo', {'photo_id': id})
            title = photo['title']['_content']
            description = photo['description']['_content']
            url = photo['urls']['url'][0]['_content']
            return {'title': title, 'description': description, 'url': url, 'cache': None}
        except:
            return None

    def make_request(self, method, expected, args={}):
        '''
        Make a request to the Flickr API
        '''
        arg_string = ""
        for arg in args:
            arg_string += '&%s=%s' % (arg, args[arg])
        key = Cache.get(self.key, decrypt=True)
        response = requests.get('https://api.flickr.com/services/rest/?method=%s&api_key=%s%s&format=json&nojsoncallback=1' % (method, key, arg_string)).json()
        if expected not in response:
            raise Exception(response)
        return response[expected]

    def select_reply(self, exclude):
        (id, image) = self.select_random_option(exclude=exclude)
        msg = '<a href="%s">📷</a>' % image['url']
        return (id, msg)

    def call(self, bot, msg, target, exclude):
        (id, text) = self.select_reply(exclude)
        bot.send_message(chat_id=msg.chat.id, text=text, reply_to_message_id=target, parse_mode='HTML')
        return [id]

    def has_effect(self):
        return True

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Send Flickr image"

    def is_private(self):
        return True

    def _to_dict(self):
        return {'key': self.key, 'pack': self.pack, 'id': self._id}

    @classmethod
    def _from_dict(cls, dict, children):
        return SendFlickr(dict['id'], dict['key'], dict['pack'])

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, Send('Please send the album ID'))
        elif stage is 1 and arg:
            if arg.text and re.match(r'[\d]+$', arg.text):
                return (2, arg.text, AskAPIKey())
            else:
                return (1, None, Send('Please send a valid ID'))
        elif stage is 2 and arg:
            return (-1, None, Done(SendFlickr(RandomMessageHandler.get_random_id(), arg, data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for sendFlickr')

    @classmethod
    def create_api(cls, stage, data, arg):
        if stage is 0:
            return (1, arg, Send('Please send me a Flickr-API key'))
        elif stage is 1:
            return (-1, None, Done( (data, arg) ))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid API key create state for sendFlickr')

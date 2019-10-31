from messageHandler import RandomMessageHandler
from cache import Cache
from logger import Logger

import requests

class SendFlickr (RandomMessageHandler):
    '''
    An action that sends images from Flickr albums when triggered.
    '''

    def __init__(self, id, api_key, pack, include=None, exclude=None):
        '''
        Initialize a FlickrAction by preloading the images in the given albums.
        '''
        super(SendFlickr, self).__init__(id, [])
        self.key = api_key
        self.pack = pack
        self.include = include
        self.exclude = exclude

        Cache.config_entry(self._id, True)
        self.update()

    def update(self):
        Logger.log_debug('Updating flickr cache')
        flickr_album = self.make_request('flickr.photosets.getPhotos', 'photoset', {'photoset_id': self.pack})
        name = flickr_album['title']
        images = list(map(lambda x: x['id'], flickr_album['photo']))

        include = self.include if self.include else images
        exclude = self.exclude if self.exclude else []
        self.add_options(images, (lambda id, self=self: self.load_image(id)), include=include, exclude=exclude)

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
        response = requests.get('https://api.flickr.com/services/rest/?method=%s&api_key=%s%s&format=json&nojsoncallback=1' % (method, self.key, arg_string)).json()
        if expected not in response:
            print('ERROR')
            print(response)
        return response[expected]

    def select_reply(self, exclude):
        (id, image) = self.select_random_option(exclude=exclude)
        msg = '<a href="%s">📷</a>' % image['url']
        return (id, msg)

    def call(self, bot, msg, target, exclude):
        (id, text) = self.select_reply(exclude)
        bot.send_message(chat_id=msg.chat.id, text=text, reply_to_message_id=target, parse_mode='HTML')
        return [id]

    def has_effect():
        return True

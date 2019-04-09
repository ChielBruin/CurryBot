from action import Action

import requests

class FlickrAction (Action):
    '''
    An action that sends images from Flickr albums when triggered.
    '''

    def __init__(self, config, api_key):
        '''
        Initialize a FlickrAction by preloading the images in the given albums.
        '''
        super(FlickrAction, self).__init__()
        self.key = api_key

        for pack in config:
            flickr_album = self.make_request('flickr.photosets.getPhotos', 'photoset', {'photoset_id': pack['imageset']})

            self.name = flickr_album['title']
            images = list(map(lambda x: x['id'], flickr_album['photo']))

            include = pack['include'] if 'include' in pack else images
            exclude = pack['exclude'] if 'exclude' in pack else []


            print('\tLoaded flickr album \'%s\' containing %d pictures' % (self.name, len(images)))
            print('\t\tPreloading images from the album (This may take a while)')
            n = self.append_ids(images, include=include, exclude=exclude, load_action=(lambda id, self=self: self.load_image(id)))
            print('\t\tPreloaded %d pictures' % n)

        print('\t%d images loaded' % len(self.ids))

    def load_image(self, id):
        '''
        Load an image from the given id.
        '''
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

    def trigger(self, bot, message, exclude=[], reply=None):
        chat_id = message.chat_id
        image_id = self.select_random_id(exclude=exclude)
        image_link = self.vals[image_id]['url']

        msg = '<a href="%s">📷</a>' % image_link
        if reply:
            bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=reply, parse_mode='HTML')
        else:
            bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML')

        return image_id

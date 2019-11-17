from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

import json
import datetime
import re
import ast

from messageHandler import MessageHandler
from logger import Logger
from cache import Cache
from configResponse import Send, Done, AskChild, AskCacheKey, AskAPIKey, NoChild, CreateException


class YtPlaylistAppend (MessageHandler):
    def __init__(self, cache_key, playlist):
        super(YtPlaylistAppend, self).__init__([])
        self.playlist = playlist
        self.authorize(cache_key)

    def authorize(self, key):
        Logger.log_debug('Authorizing youtube API')
        try:
            api_service_name = 'youtube'
            api_version = 'v3'

            credentials_dict = ast.literal_eval(Cache.get(key, decrypt=True))
            credentials = Credentials(
                credentials_dict["token"],
                refresh_token = credentials_dict["refresh_token"],
                token_uri = credentials_dict["token_uri"],
                client_id = credentials_dict["client_id"],
                client_secret = credentials_dict["client_secret"],
                scopes = credentials_dict["scopes"]
            )

            self.youtube = googleapiclient.discovery.build(
                'youtube', 'v3', credentials=credentials
            )
        except Exception as ex:
            Logger.log_exception(ex, msg='Error while authorizing Youtube API')


    def _playlist_add(self, video_id):
        request = self.youtube.playlistItems().insert(
        part='snippet',
        body={
          'snippet': {
            'playlistId': self.playlist,
            'position': 0,
            'resourceId': {
              'kind': 'youtube#video',
              'videoId': video_id
              }
          }
        }
        )
        response = request.execute()

    def call(self, bot, msg, reply_to, exclude):
        self._playlist_add(msg.text)
        return []

    @classmethod
    def is_entrypoint(cls):
        return False

    @classmethod
    def get_name(cls):
        return "Add video to Youtube playlist"

    @classmethod
    def create(cls, stage, data, arg):
        if stage is 0:
            return (1, None, Send('What is the id of the YouTube playlist?'))
        elif stage is 1 and arg:
            if arg.text and re.match(r'[A-Za-z0-9_-]{10,}', arg.text):
                return (2, arg.text, AskAPIKey())
            else:
                return (1, None, Send('Invalid id, please try again'))
        elif stage is 2 and arg:
            return (-1, None, Done(YtPlaylistAppend(arg, data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for ytPlaylistAppend')

    @classmethod
    def create_api(cls, stage, data, arg):
        if stage is 0:
            return (1, arg, Send('Please send me the contents of your secrets.json'))
        elif stage is 1:
            try:
                secret = json.loads(arg)
                scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
                flow = InstalledAppFlow.from_client_config(secret, scopes)

                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                url, state = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true'
                )
                return (2, (data, flow), Send('Please visit %s, login and send me the access code' % url))
            except json.JSONDecodeError as ex:
                return (1, data, Send('Invalid JSON, please try again'))
        elif stage is 2:
            (name, flow) = data
            try:
                flow.fetch_token(code=arg)
                credentials = cls._credentials_to_dict(flow.credentials)
                return (-1, None, Done( (name, str(credentials)) ))
            except Exception:
                return (2, data, Send('Error while processing response, please try again'))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid API key create state for ytPlaylistAppend')

    @classmethod
    def _credentials_to_dict(cls, credentials):
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

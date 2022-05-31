import json
import re
import ast
import errno

import googleapiclient.discovery
import googleapiclient.errors
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

from currybot.handlers.messageHandler import MessageHandler
from currybot.data.logger import Logger
from currybot.data.cache import Cache
from currybot.configResponse import Send, Done, AskAPIKey, CreateException


class YtPlaylistAppend(MessageHandler):
    def __init__(self, cache_key, playlist):
        super(YtPlaylistAppend, self).__init__([])
        self.playlist = playlist
        self.cache_key = cache_key
        self.authorize()

    def authorize(self):
        Logger.log_debug('Authorizing YouTube API')
        try:
            credentials_dict = ast.literal_eval(Cache.get(self.cache_key, decrypt=True))
            credentials = Credentials(
                credentials_dict["token"],
                refresh_token=credentials_dict["refresh_token"],
                token_uri=credentials_dict["token_uri"],
                client_id=credentials_dict["client_id"],
                client_secret=credentials_dict["client_secret"],
                scopes=credentials_dict["scopes"]
            )
            self.credentials = credentials
            self.youtube = googleapiclient.discovery.build(
                'youtube', 'v3', credentials=credentials, cache_discovery=False
            )
        except Exception as ex:
            Logger.log_exception(ex, msg='Error while authorizing YouTube API')

    def _playlist_add(self, video_id, chat_id, attempts=0):
        try:
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
        except IOError as ex:
            # On Broken Pipe error, retry
            if ex.errno == errno.EPIPE:
                if attempts < 3:
                    self._playlist_add(video_id, chat_id, attempts=attempts+1)
                else:
                    Logger.log_error('Adding YouTube video to playlist failed with broken pipe', chat=chat_id)

    def call(self, bot, message, reply_to, exclude):
        if not message.text:
            raise Exception('An empty message is not a valid video ID')
        self._playlist_add(message.text, message.chat.id)
        return []

    @classmethod
    def is_entrypoint(cls):
        return False

    def is_private(self):
        return True

    @classmethod
    def get_name(cls):
        return "Add video to YouTube playlist"

    @classmethod
    def create(cls, stage, data, arg):
        if stage == 0:
            return (1, None, Send('What is the id of the YouTube playlist?'))
        elif stage == 1 and arg:
            if arg.text and re.match(r'[A-Za-z0-9_-]{10,}', arg.text):
                return (2, arg.text, AskAPIKey())
            else:
                return (1, None, Send('Invalid id, please try again'))
        elif stage == 2 and arg:
            return (-1, None, Done(YtPlaylistAppend(arg, data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for ytPlaylistAppend')

    @classmethod
    def create_api(cls, stage, data, arg):
        if stage == 0:
            return (1, arg, Send('Please send me the contents of your secrets.json'))
        elif stage == 1:
            try:
                secret = json.loads(arg)
                scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
                flow = InstalledAppFlow.from_client_config(secret, scopes)

                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                url, _ = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true'
                )
                return (2, (data, flow), Send('Please visit %s, login and send me the access code' % url))
            except json.JSONDecodeError:
                return (1, data, Send('Invalid JSON, please try again'))
        elif stage == 2:
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

    def on_update(self, bot):
        credentials = self._credentials_to_dict(self.credentials)
        Cache.put(self.cache_key, str(credentials), encrypt=True)

    @classmethod
    def _from_dict(cls, dict, children):
        key = dict['key']
        playlist = dict['playlist']
        return YtPlaylistAppend(key, playlist)

    def _to_dict(self):
        return {
            'key': self.cache_key,
            'playlist': self.playlist
        }

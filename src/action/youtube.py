import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

import json
import datetime

from action.action import Action
from logger import Logger
from cache import Cache


class YtPlaylistAppendAction (Action):
    def __init__(self, id, api_key, playlist, index=0):
        super(YtPlaylistAppendAction, self).__init__(id)
        self.index = index
        self.playlist = playlist
        self.youtube = self.authorize(api_key)

    def encode_credentials(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.timestamp()
        return json.JSONEncoder.default(self, obj)

    def authorize(self, secret_file):
        Logger.log('DEBUG', 'Authorizing youtube API')
        try:
            c_json = Cache.credentials_get_cache(self.id)
            api_service_name = "youtube"
            api_version = "v3"

            if c_json is None:
                scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    secret_file, scopes)
                credentials = flow.run_console()
            else:
                Logger.log('DEBUG', 'Using cached credentials')
                c_dict = json.loads(c_json)
                credentials = Credentials(
                                token=c_dict['token'],
                                refresh_token=c_dict['_refresh_token'],
                                token_uri=c_dict['_token_uri'],
                                client_id=c_dict['_client_id'],
                                client_secret=c_dict['_client_secret'],
                                scopes=c_dict['_scopes'])
                credentials.expiry = datetime.datetime.fromtimestamp(c_dict['expiry'])

            Cache.credentials_put_cache(self.id, json.dumps(credentials.__dict__, default=self.encode_credentials))

            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, credentials=credentials)
            return youtube

        except Exception as ex:
            Logger.log_exception('ERROR', ex, msg='Error while authorizing Youtube API')


    def _playlist_add(self, video_id):
        request = self.youtube.playlistItems().insert(
        part='snippet',
        body={
          'snippet': {
            'playlistId': self.playlist,
            'position': self.index,
            'resourceId': {
              'kind': 'youtube#video',
              'videoId': video_id
              }
          }
        }
        )
        response = request.execute()

    def dispatch(self, bot, msg, exclude):
        self._playlist_add(msg.text)
        bot.send_message(chat_id=msg.chat.id, text='Playlist updated')
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        self._playlist_add(msg.text)
        bot.send_message(chat_id=msg.chat.id, text='Playlist updated', reply_to_message_id=reply_to)
        return []

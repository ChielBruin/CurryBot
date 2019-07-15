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
        (self.credentials, self.youtube) = self.authorize(api_key)
        self.update()

    def encode_credentials(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.timestamp()
        return json.JSONEncoder.default(self, obj)

    def authorize(self, secret_file):
        Logger.log_debug('Authorizing youtube API')
        try:
            c_json = Cache.shared_get_cache_encrypted(self.id)
            api_service_name = "youtube"
            api_version = "v3"

            if c_json is None:
                scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    secret_file, scopes)
                credentials = flow.run_console()
            else:
                Logger.log_debug('Using cached credentials')
                c_dict = json.loads(c_json)
                credentials = Credentials(
                                token=c_dict['token'],
                                refresh_token=c_dict['_refresh_token'],
                                token_uri=c_dict['_token_uri'],
                                client_id=c_dict['_client_id'],
                                client_secret=c_dict['_client_secret'],
                                scopes=c_dict['_scopes'])
                credentials.expiry = datetime.datetime.fromtimestamp(c_dict['expiry'])

            youtube = googleapiclient.discovery.build(
                api_service_name, api_version, credentials=credentials)
            return (credentials, youtube)

        except Exception as ex:
            Logger.log_exception(ex, msg='Error while authorizing Youtube API')


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

    def update(self):
        credentials_json = json.dumps(self.credentials.__dict__, default=self.encode_credentials)
        Cache.shared_put_cache_encrypted(self.id, credentials_json)

    def dispatch(self, bot, msg, exclude):
        self._playlist_add(msg.text)
        return []

    def dispatch_reply(self, bot, msg, reply_to, exclude):
        self._playlist_add(msg.text)
        return []

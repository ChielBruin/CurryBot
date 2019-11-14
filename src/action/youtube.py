import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

import json
import datetime
import re

from messageHandler import MessageHandler
from logger import Logger
from cache import Cache
from configResponse import Send, Done, AskChild, NoChild, CreateException


class YtPlaylistAppend (MessageHandler):
    def __init__(self, key_key, playlist):
        super(YtPlaylistAppend, self).__init__([])
        self.playlist = playlist
        self.authorize(key_key)

    def authorize(self, key):
        Logger.log_debug('Authorizing youtube API')
        try:
            api_service_name = 'youtube'
            api_version = 'v3'

            self.youtube = googleapiclient.discovery.build(
                api_service_name, api_version, developerKey = Cache.get(key, encrypted=True)
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
            if arg.text and re.matches(r'[A-Za-z0-9_-]{5,}', arg.text):
                return (2, arg.text, AskCacheKey(is_local=True))
            else:
                return (1, None, Send('Invalid id, please try again'))
        elif stage is 2 and arg:
            return (-1, None, Done(YtPlaylistAppend(arg, data)))
        else:
            print(stage, data, arg)
            raise CreateException('Invalid create state for userJoinedChat')

from sideEffect import SideEffect

import os, re

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

class YtPlaylistAppend (SideEffect):
    '''
    A side-effect that can add videos to YouTube playlists.
    '''
    _youtube = {}

    def __init__(self, config, secret):
        self.regex = '(https?://)?(www\.)?youtu((.be/)|(be.(com|nl)/watch\?v=))([a-zA-z0-9\_\-]+)'

        self.index = config['index'] if 'index' in config else 0
        self.playlist_id = config['playlist-id']
        self.youtube = YtPlaylistAppend.authorize(secret)

    @classmethod
    def authorize(cls, secret_location):
        '''
        Get credentials for a given secret.
        Caches the authorization for reuse.
        '''
        if secret_location not in cls._youtube:
            scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
            api_service_name = 'youtube'
            api_version = 'v3'
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                secret_location, scopes)

            credentials = flow.run_console()
            cls._youtube[secret_location] = googleapiclient.discovery.build(
                api_service_name, api_version, credentials=credentials)

        return cls._youtube[secret_location]

    def trigger(self, message):
        '''
        Find the video ID and add it to the playlist
        '''
        match = re.search(self.regex, message.text)
        if not match:
            return

        video_id = match.group(7)

        request = self.youtube.playlistItems().insert(
        part='snippet',
        body={
          'snippet': {
            'playlistId': self.playlist_id,
            'position': self.index,
            'resourceId': {
              'kind': 'youtube#video',
              'videoId': video_id
              }
          }
        }
        )
        response = request.execute()

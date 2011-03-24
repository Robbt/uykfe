
from time import time, sleep
from json import loads
from logging import getLogger
from urllib.parse import urlunparse, quote
from urllib.request import Request, urlopen

from uykfe.support.config import SECRET, PROXY, lastfm


LOG = getLogger(__name__)


class NotFoundError(Exception):
    pass


def unpack(map, *names):
    if names:
        try:
            return unpack(map[names[0]], *names[1:])
        except TypeError:
            raise NotFoundError
    else:
        return map
    
def possible_list(value):
    if isinstance(value, list):
        return value
    else:
        return [value]
    

class LastFm():
    
    def __init__(self, secret=None, proxy=None, dir=None, name=None):
        self.__api_key = '542c2f7c651d929ece5a72f18db35a93'
        if not secret:
            lastfm_config = lastfm(dir=dir, name=name)
            secret = lastfm_config[SECRET]
            proxy = lastfm_config.get(PROXY, None)
        self.__secret = secret
        self.__proxy = proxy
        self.__timestamp = None
    
    def __url(self, **kargs):
        kargs['api_key'] = self.__api_key
        kargs['format'] = 'json'
        query = '&'.join(name + '=' + quote(kargs[name], encoding='utf8') for name in kargs)
        url = urlunparse(('http', 'ws.audioscrobbler.com', '2.0/', '', query, ''))
        LOG.debug('URL: {0}'.format(url))
        return url
    
    def __request(self, **kargs):
        request = Request(self.__url(**kargs),
                          headers={'User-Agent': 'Uykfe (andrew@acooke.org)'})
        if self.__proxy:
            request.set_proxy(self.__proxy, 'http')
        return request
        
    def __read(self, **kargs):
        now = time()
        while self.__timestamp and now - self.__timestamp < 0.2:
            sleep(0.1)
        self.__timestamp = time()
        response = loads(urlopen(self.__request(**kargs)).read().decode('utf8'))
        LOG.debug(response)
        return response
        
    def track_search(self, track):
        return self.__read(method='track.search', track=track)
    
    def artists_for_track(self, track):
        response = self.track_search(track)
        for track in possible_list(unpack(response, 'results', 'trackmatches', 'track')):
            yield track['artist']

    def artist_search(self, artist):
        return self.__read(method='artist.search', artist=artist)
    
    def artist_for_artist(self, artist):
        return possible_list(unpack(self.artist_search(artist), 'results', 'artistmatches', 'artist'))[0]['name']
    
        
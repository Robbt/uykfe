
from time import time, sleep
from json import loads
from logging import getLogger
from urllib.parse import urlunparse, quote
from urllib.request import Request, urlopen

from uykfe.support.config import SECRET, PROXY, lastfm_kargs
from urllib.error import HTTPError
from http.client import BadStatusLine


LOG = getLogger(__name__)


class NotFoundError(Exception):
    pass


def unpack(map, *names):
    if names:
        try:
            return unpack(map[names[0]], *names[1:])
        except TypeError:
            raise NotFoundError
        except KeyError:
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
            secret = lastfm_kargs(dir=dir, name=name)[SECRET]
            proxy = lastfm_kargs(dir=dir, name=name)[PROXY]
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
        while self.__timestamp and time() - self.__timestamp < 1:
            LOG.debug('sleep')
            sleep(0.3)
        self.__timestamp = time()
        for retry in range(10):
            try:
                response = urlopen(self.__request(**kargs))
                break
            except (HTTPError, BadStatusLine) as e:
                LOG.warn(e)
                sleep(60*2**retry)
        #LOG.debug(response)
        result = loads(response.read().decode('utf8'))
        #LOG.debug(result)
        return result
        
    def track_search(self, track):
        return self.__read(method='track.search', track=track)
    
    def artists_for_track(self, track):
        response = self.track_search(track)
        for track in possible_list(unpack(response, 'results', 'trackmatches', 'track')):
            yield track['artist']

    def artist_search(self, artist):
        return self.__read(method='artist.search', artist=artist)
    
    def artists_for_artist(self, artist):
        for artist in possible_list(unpack(self.artist_search(artist), 'results', 'artistmatches', 'artist')):
            yield artist['name']
    
    def artist_tags(self, artist):
        return self.__read(method='artist.gettoptags', artist=artist)
    
    def tags_for_artist(self, artist):
        def totuple(tagdata):
            return (tagdata['name'], int(tagdata['count']))
        def nonzero(tagdata):
            return tagdata[1] > 0
        data = possible_list(unpack(self.artist_tags(artist), 'toptags', 'tag'))
        return filter(nonzero, map(totuple, data))

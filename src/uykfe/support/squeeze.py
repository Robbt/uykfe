
from logging import getLogger
from telnetlib import Telnet
from urllib.parse import quote, unquote

from uykfe.support.config import squeeze_kargs, ADDRESS, PORT, PLAYER


LOG = getLogger(__name__)


class SqueezeServer():
    
    def __init__(self, address=None, port=None, player=None, dir=None, name=None):
        address = address or squeeze_kargs(dir, name)[ADDRESS]
        port = port or squeeze_kargs(dir, name)[PORT]
        player = player or squeeze_kargs(dir, name)[PLAYER]
        LOG.debug('Connecting to {0}:{1}.'.format(address, port))
        self.__telnet = Telnet(address, port) 
        LOG.debug('Connected.')
        self.__pid = self.player_ids[player]
        LOG.debug('Found player {0} at {1}'.format(player, self.__pid))
    
    @property
    def player_ids(self):
        ids = {}
        for i in range(int(self.__global('player count ?'))):
            id = self.__global('player id {0} ?'.format(i))
            name = self.__global('player name {0} ?'.format(i))
            ids[name] = id
        return ids
    
    @property
    def playlist_tracks(self):
        return int(self.__player('playlist tracks ?'))
    
    @property
    def playlist_index(self):
        return int(self.__player('playlist index ?'))
    
    @property
    def playlist_remaining(self):
        return self.playlist_tracks - self.playlist_index 
    
    def __global(self, command):
        command = command.encode('utf8')
        if command.endswith(b'?'):
            response = command[:-1]
        else:
            response = b''
        response += b'([^\n]*)\n'
        LOG.debug('Sending {0}'.format(command))
        self.__telnet.write(command + b'\n')
        (_, match, _) = self.__telnet.expect([response])
        result = unquote(match.groups(1)[0].decode('utf8'), 'utf8')
        LOG.debug('Received: {0}'.format(result))
        return result
    
    def __player(self, command):
        return self.__global(quote(self.__pid) + ' ' + command)

    def playlist_add(self, url):
        LOG.info('Adding {0}.'.format(url))
        return unquote(self.__player('playlist add {0}'.format(quote(url))))
    
    @property
    def path(self):
        return unquote(self.__player('path ?'))
    
    @property
    def url(self):
        path = self.path
        if not path.startswith('file://'):
            path = 'file://' + path
        return path

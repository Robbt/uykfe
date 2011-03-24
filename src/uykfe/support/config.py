
from json import dump, load
from logging import getLogger
from os import getcwd, remove, environ
from os.path import join, exists


CONFIG_NAME = '.uykferc'
CONFIG_ENVDIR = 'UYKFE_DIR'
LOG = getLogger(__name__)
MP3DIRS = 'mp3_dirs'
SERVER = 'server'
ADDRESS = 'address'
PORT = 'port'
PLAYER = 'player'
LASTFM = 'lastfm'
SECRET = 'secret'
PROXY = 'proxy'
EXAMPLE = {MP3DIRS: ['add directories', 'with mp3 files'],
           SERVER: {ADDRESS: 'address of squeeze server',
                    PORT: 9090,
                    PLAYER: 'player name'},
           LASTFM: {SECRET: 'lastfm api secret',
                    PROXY: 'optional proxy url'}}


def config_path(dir=None, name=None):
    return join(dir or environ.get(CONFIG_ENVDIR, getcwd()), name or CONFIG_NAME)


def delete_config(dir=None, name=None):
    path = config_path(dir, name)
    if exists(path):
        LOG.warn('Deleting configuration {0}.'.format(path))
        remove(path)
    else:
        LOG.debug('No configuration at {0} to delete.'.format(path))
    

def open_config(dir=None, name=None):
    path = config_path(dir, name)
    if not exists(path):
        LOG.error('No configuration at {0}.'.format(path))
        LOG.error('Writing default; edit and restart.')
        with open(path, 'w') as sink:
            dump(EXAMPLE, sink, indent=2)
            exit()
    with open(path) as source:
        return load(source)


def mp3_dirs(config=None, dir=None, name=None):
    config = config or open_config(dir, name)
    if MP3DIRS not in config: config[MP3DIRS] = []
    return config[MP3DIRS]


def server(config=None, dir=None, name=None):
    config = config or open_config(dir, name)
    if SERVER not in config: config[SERVER] = {}
    server = config[SERVER]
    if ADDRESS not in server: server[ADDRESS] = '10.2.0.9'
    if PORT not in server: SERVER[PORT] = 9090
    if PLAYER not in server: SERVER[PLAYER] = 'HiFi'
    return server


def require(config, name):
    if name not in config:
        raise Exception('Must have {0} in configuration'.format(name))
    return config[name]


def lastfm(config=None, dir=None, name=None):
    config = config or open_config(dir, name)
    lastfm = require(config, LASTFM)
    require(lastfm, SECRET)
    return lastfm

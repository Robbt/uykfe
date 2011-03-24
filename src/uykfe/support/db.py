
from logging import getLogger
from os import getcwd, remove, environ
from os.path import join, exists
from urllib.parse import urlunparse

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import OperationalError

from uykfe.support.config import CONFIG_ENVDIR
from sqlalchemy.orm import relationship


DB_NAME = 'uykfe.db'
LOG = getLogger(__name__)
BASE = declarative_base()


def db_path(dir=None, name=None):
    return join(dir or environ.get(CONFIG_ENVDIR, getcwd()), name or DB_NAME)


def get_engine(dir=None, name=None):
    path = db_path(dir, name)
    url = urlunparse(('sqlite', '/', path, '', '', ''))
    LOG.debug('Creating engine for {0}.'.format(url))
    return create_engine(url)


def get_session_factory(engine=None, dir=None, name=None):
    engine = engine or get_engine(dir, name)
    return sessionmaker(bind=engine)


def create_db(engine=None, dir=None, name=None):
    engine = engine or get_engine(dir, name)
    LOG.info('Creating metadata.')
    BASE.metadata.create_all(engine)
    
    
def open_db(engine=None, dir=None, name=None):
    '''return a session factory, creating the DB if necessary first'''
    engine = engine or get_engine(dir, name)
    session = get_session_factory(engine)
    try:
        session().query(LocalArtist).count()
    except OperationalError:
        create_db(engine)
        session = get_session_factory(engine)
    return session


def delete_db(dir=None, name=None):
    path = db_path(dir, name)
    if exists(path):
        LOG.warn('Deleting database {0}.'.format(path))
        remove(path)
    else:
        LOG.debug('No database at {0} to delete.'.format(path))
    

class LocalArtist(BASE):
    
    __tablename__ = 'local_artists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True)
    lastfm_artist_id = Column(Integer, ForeignKey('lastfm_artists.id'), nullable=True)
    tracks = relationship('LocalTrack', backref='local_artist')
    
    def __init__(self, name, lastfm_artist=None):
        self.name = name
        self.lastfm_artist = lastfm_artist
    

class LocalTrack(BASE):
    
    __tablename__ = 'local_tracks'

    url = Column(String, primary_key=True)
    name = Column(String)
    local_artist_id = Column(Integer, ForeignKey('local_artists.id'))

    def __init__(self, url, name, local_artist):
        self.url = url
        self.name = name
        self.local_artist = local_artist

    def __repr__(self):
        return '<LocalTrack {0}>'.format(self.url)


class LastFmArtist(BASE):
    
    __tablename__ = 'lastfm_artists'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True)
    local_artists = relationship('LocalArtist', backref='lastfm_artist')
    lastfm_tagweights = relationship('LastFmTagWeight', backref='lastfm_artist')
    
    def __init__(self, name):
        self.name = name


class LastFmTagWord(BASE):
    
    __tablename__ = 'lastfm_tagwords'

    id = Column(Integer, primary_key=True)
    word = Column(String, index=True, unique=True)
    lastfm_tagweights = relationship('LastFmTagWeight', backref='lastfm_tagword')
    
    def __init__(self, word):
        self.word = word


class LastFmTagWeight(BASE):
    
    __tablename__ = 'lastfm_tagweights'

    lastfm_artist_id = Column(Integer, ForeignKey('lastfm_artists.id'), primary_key=True)
    lastfm_tagword_id = Column(Integer, ForeignKey('lastfm_tagwords.id'), primary_key=True)
    weight = Column(Integer)
    
    def __init__(self, weight, lastfm_tagword=None, lastfm_artist=None):
        self.weight = weight
        self.lastfm_tagword = lastfm_tagword
        self.lastfm_artist = lastfm_artist
        
    
    
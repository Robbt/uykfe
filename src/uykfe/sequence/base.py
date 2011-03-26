
from abc import abstractmethod, abstractproperty
from logging import getLogger
from random import random

from uykfe.support.db import LocalTrack
from sqlalchemy.orm.exc import NoResultFound


LOG = getLogger(__name__)


class State():
    
    @abstractproperty
    def current_url(self): pass
    
    @abstractproperty
    def session(self): pass
    

class Control():
    
    @abstractmethod
    def weight_options(self, state, graphs): pass
    
    @abstractmethod
    def select_track(self, state, lastfm_artist): pass
    
    @abstractmethod
    def random_track(self, state): pass
    
    
    
def sequence(state, control):
    while True:
        current_url = state.current_url
        if not current_url:
            LOG.info('No current file.')
            yield control.random_track(state)
        else:
            yield from_graph(state, control, current_url)
        
        
def from_graph(state, control, current_url):
    try:
        track = state.session.query(LocalTrack).filter(LocalTrack.url == current_url).one()
        graphs = track.local_artist.lastfm_artist.graph_out
        weighted_artists = list(control.weight_options(state, graphs))
        LOG.debug(weighted_artists)
        total_weight = sum(map(lambda x: x[0], weighted_artists))
        index = total_weight * random()
        while weighted_artists:
            (weight, artist) = weighted_artists.pop()
            LOG.debug('{0} at {1}: {2}'.format(index, weight, artist.name))
            index -= weight
            if index <= 0:
                return control.select_track(state, artist)
        LOG.error('Weighting failed.')
        exit()
    except NoResultFound:
        LOG.warn('Could not find {0}.'.format(current_url))
        return control.random_track(state)

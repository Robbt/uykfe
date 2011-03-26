
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
    
    @abstractmethod
    def record_track(self, track): pass
    

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
            track = control.random_track(state)
        else:
            track = from_graph(state, control, current_url)
        state.record_track(track)
        yield track
        
        
def from_graph(state, control, current_url):
    try:
        track = state.session.query(LocalTrack).filter(LocalTrack.url == current_url).one()
        graphs = track.local_artist.lastfm_artist.graph_out
        if not graphs:
            LOG.warn('No routes from {0}.'.format(track.local_artist.name))
            return control.random_track(state)
        weighted_artists = list(control.weight_options(state, graphs))
        total_weight = sum(map(lambda x: x[0], weighted_artists))
        weighted_artists = [(weight / total_weight, artist) for (weight, artist) in weighted_artists]
        weighted_artists.sort(key=lambda x: x[0], reverse=True)
        for (weight, artist) in weighted_artists:
            LOG.debug('{0:3.2f} {1}'.format(weight, artist.name[0:60]))
        index = random()
        while weighted_artists:
            (weight, artist) = weighted_artists.pop()
            index -= weight
            if index <= 0:
                return control.select_track(state, artist)
        LOG.error('Weighting failed.')
        exit()
    except NoResultFound:
        LOG.warn('Could not find {0}.'.format(current_url))
        return control.random_track(state)


from random import shuffle

from uykfe.sequence.base import State
from uykfe.support.db import LocalTrack



class DbState(State):
    
    def __init__(self, session):
        self.__session = session
        all_tracks = list(session.query(LocalTrack).all())
        shuffle(all_tracks)
        self.unplayed_tracks = set(all_tracks)
        self.history = []
        
    @property
    def session(self):
        return self.__session
    
    def record_track(self, track):
        self.history.append(track)
        

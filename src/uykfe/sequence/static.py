
from uykfe.sequence.db import DbState, DbControl



class StaticState(DbState):
    
    def __init__(self, session):
        super(StaticState, self).__init__(session)
        self.__current_url = None
        
    @property
    def current_url(self):
        return self.__current_url

    @current_url.setter
    def current_url(self, url):
        self.__current_url = url


class StaticControl(DbControl):
    
    def select_track(self, state, lastfm_artist):
        track = super(StaticControl, self).select_track(state, lastfm_artist)
        state.current_url = track.url
        return track
    
    def random_track(self, state):
        track = super(StaticControl, self).random_track(state)
        state.current_url = track.url
        return track


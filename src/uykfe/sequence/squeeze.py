
from time import sleep

from uykfe.sequence.db import DbState


class SqueezeState(DbState):
    
    def __init__(self, session, limit, squeeze):
        super(SqueezeState, self).__init__(session, limit)
        self.__squeeze = squeeze
        
    @property
    def current_url(self):
        if self.__squeeze.playlist_remaining:
            return self.__squeeze.url
        else:
            return None
    
    def wait(self):
        while self.__squeeze.playlist_remaining > 1:
            sleep(1)

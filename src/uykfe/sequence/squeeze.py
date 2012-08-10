
from time import sleep
from logging import getLogger

from sqlalchemy.orm.exc import NoResultFound

from uykfe.sequence.static import StaticState
from uykfe.support.db import LocalTrack


LOG = getLogger(__name__)


class SqueezeState(StaticState):
    
    def __init__(self, session, limit, squeeze):
        super(SqueezeState, self).__init__(session, limit)
        self.__squeeze = squeeze
        
    @property
    def current_url(self):
        if self.__squeeze:
            if self.__squeeze.playlist_remaining:
                return self.__squeeze.url
            else:
                return None
        else:
            return super(SqueezeState, self).current_url
    
    def wait(self):
        reset = self.__squeeze.playlist_remaining > 2
        while self.__squeeze.playlist_remaining > 1:
            sleep(1)
        if reset or not self.history:
            url = self.current_url
            if url:
                try:
                    track = self.session.query(LocalTrack).filter(LocalTrack.url == url).one()
                    LOG.info('Resetting to {0}'.format(track.local_artist.name))
                    self.history=[track]
                except NoResultFound:
                    pass

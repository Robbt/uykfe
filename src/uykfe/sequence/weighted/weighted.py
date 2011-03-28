
from logging import getLogger

from sqlalchemy.sql.functions import max as max_
from sqlalchemy.orm.exc import NoResultFound

from uykfe.support.db import Graph
from uykfe.sequence.db import DbControl
from sqlalchemy.sql.expression import and_, or_


LOG = getLogger(__name__)


def normalize(weight, exponent, max_weight):
    return (1 + weight / max_weight) ** exponent / 2 ** exponent


class WeightedControl(DbControl):
    
    def __init__(self, state, x_next, depth, x_depth, directed, neighbour):
        super(WeightedControl, self).__init__(directed)
        self.__x_next = x_next
        self.__depth = depth
        self.__x_depth = x_depth
        self.__neighbour = neighbour
        self.__max_weight = state.session.query(max_(Graph.weight)).one()[0]
        
    def weighted_artists(self, state, track):

        if self.__depth and len(state.history) > self.__depth:
            previous = state.history[-self.__depth].local_artist.lastfm_artist
        else:
            previous = None

        weighted_artists = list(super(WeightedControl, self).weighted_artists(state, track))
        if not weighted_artists:
            return
        unplayed = dict((artist, self._unplayed(state, artist)) for (_, artist) in weighted_artists)
        max_unplayed = max(unplayed.values())
        unplayed = dict((artist, unplayed[artist] / max_unplayed) for (_, artist) in weighted_artists)
        
        for (weight, artist) in weighted_artists:
            weight = normalize(weight, self.__x_next, self.__max_weight) * unplayed[artist]
            if self.__neighbour:
                outgoing = len(artist.graph_out)
                if not self._directed:
                    outgoing += len(artist.graph_in)
                weight /= outgoing
            depth_weight = 0
            if previous:
                if previous == artist:
                    depth_weight = self.__max_weight
                else:
                    try:
                        q = state.session.query(Graph.weight)
                        q = q.filter(or_(and_(Graph.from_ == previous and Graph.to_ == artist),
                                         and_(Graph.from_ == artist and Graph.to_ == previous)))
                        depth_weight = max(map(lambda r: r[0], q.all()))
                    except NoResultFound:
                        LOG.debug('No link from {0} to {1}.'.format(previous.name, artist.name))
                        depth_weight = 0
            weight *= normalize(depth_weight, self.__x_depth, self.__max_weight)
            #LOG.debug(str(weight) + ' ' + artist.name)
            yield (weight, artist)
    

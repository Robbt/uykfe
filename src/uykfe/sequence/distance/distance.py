
from logging import getLogger

from sqlalchemy.sql.functions import max as max_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_
from networkx import DiGraph, Graph as Graph_, all_pairs_shortest_path_length

from uykfe.support.db import Graph, LastFmArtist
from uykfe.sequence.db import DbControl
from uykfe.sequence.squeeze import SqueezeState


LOG = getLogger(__name__)


def normalize(weight, exponent, max_weight):
    return (1 + weight / max_weight) ** exponent / 2 ** exponent


class DistanceState(SqueezeState):
    
    def __init__(self, session, limit, directed, squeeze=None):
        super(DistanceState, self).__init__(session, limit, squeeze)
        self.distances = self.build_distances(session, limit, directed,)
        
    def build_distances(self, session, limit, directed):
        if directed:
            graph = DiGraph()
        else:
            graph = Graph_()
        for node in session.query(LastFmArtist).all():
            for edge in node.graph_out[0:self.limit]:
                graph.add_edge(edge.from_.id, edge.to_.id)
        self.__distances = all_pairs_shortest_path_length(graph)
        self.max_distance = max(max(self.__distances[key]) for key in self.__distances)
        LOG.debug('Max distance: {0}'.format(self.max_distance))
    
    def distance(self, from_, to_):
        try:
            return self.__distances[from_.id][to_.id]
        except KeyError:
            return self.max_distance


class DistanceControl(DbControl):
    
    def __init__(self, state, x_next, depth, x_depth, directed, neighbour):
        super(DistanceControl, self).__init__(directed)
        self.__x_next = x_next
        self.__depth = depth
        self.__x_depth = x_depth
        self.__neighbour = neighbour
        self.__max_weight = state.session.query(max_(Graph.weight)).one()[0]
        
    def weighted_artists(self, state, track):

        if self.__depth is not None and len(state.history) > self.__depth:
            previous = state.history[-self.__depth].local_artist.lastfm_artist
            LOG.info('Distances to {0}'.format(previous.name))
        else:
            previous = None

        weighted_artists = list(super(DistanceControl, self).weighted_artists(state, track))
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
            distance_weight = 1
            if previous:
                distance_weight = 1 + state.distance(previous, artist)
#            distance_weight = normalize(distance_weight, self.__x_depth, state.max_distance)
            distance_weight **= self.__x_depth
            weight /= distance_weight
            LOG.debug('{0} ({1}) {2}'.format(weight, distance_weight, artist.name))
            yield (weight, artist)
    

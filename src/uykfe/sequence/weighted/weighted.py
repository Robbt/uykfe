
from logging import getLogger

from sqlalchemy.sql.functions import max as max_
from sqlalchemy.orm.exc import NoResultFound

from uykfe.support.db import Graph
from uykfe.sequence.db import DbControl


LOG = getLogger(__name__)


def normalize(weight, exponent, max_weight):
    return (1 + weight / max_weight) ** exponent / 2 ** exponent


class WeightedControl(DbControl):
    
    def __init__(self, state, x_next, depth, x_depth):
        self.__x_next = x_next
        self.__depth = depth
        self.__x_depth = x_depth
        self.__max_weight = state.session.query(max_(Graph.weight)).one()[0]
        
    def weight_options(self, state, graphs):
        
        def count_unplayed(graph):
            unplayed = 0
            for artist in graph.to_.local_artists:
                for track in artist.tracks:
                    if track in state.unplayed_tracks:
                        unplayed += 1
            return unplayed
        unplayed = dict((graph, count_unplayed(graph)) for graph in graphs)
        max_unplayed = max(unplayed.values())
        unplayed = dict((graph, unplayed[graph] / max_unplayed) for graph in graphs)
        
        if self.__depth and len(state.history) > self.__depth:
            previous = state.history[-self.__depth].local_artist.lastfm_artist
        else:
            previous = None
            
        for graph in graphs:
            weight = normalize(graph.weight, self.__x_next, self.__max_weight) * unplayed[graph]
            depth_weight = 0
            if previous:
                if previous == graph.to_:
                    depth_weight = self.__max_weight
                else:
                    try:
                        q = state.session.query(Graph.weight)
                        q = q.filter(Graph.from_ == previous)
                        q = q.filter(Graph.to_ == graph.to_)  
                        depth_weight = q.one()[0]
                    except NoResultFound:
                        LOG.debug('No link from {0} to {1}.'.format(previous.name, graph.to_.name))
                        depth_weight = 0
            weight *= normalize(depth_weight, self.__x_depth, self.__max_weight)
            yield (weight, graph.to_)
    

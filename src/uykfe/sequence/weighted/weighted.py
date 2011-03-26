
from logging import getLogger

from sqlalchemy.sql.functions import max as max_
from sqlalchemy.orm.exc import NoResultFound

from uykfe.support.db import Graph
from uykfe.sequence.db import DbControl


LOG = getLogger(__name__)


class WeightedControl(DbControl):
    
    def __init__(self, state, x_next, depth, x_depth):
        self.__x_next = x_next
        self.__depth = depth
        self.__x_depth = x_depth
        self.__max_weight = state.session.query(max_(Graph.weight)).one()[0]
        
    def __normalize(self, weight, exponent):
        normalized = (1 + weight / self.__max_weight) ** exponent
        #LOG.debug('{0:7.1f} -> {1:4.2f}'.format(weight, normalized))
        return normalized
    
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
            weight = self.__normalize(graph.weight, self.__x_next) * unplayed[graph]
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
            weight *= self.__normalize(depth_weight, self.__x_depth)
            yield (weight, graph.to_)
    

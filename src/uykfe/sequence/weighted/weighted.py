
from logging import getLogger
from random import shuffle
from sqlalchemy.sql.functions import max as max_

from uykfe.sequence.base import Control
from uykfe.support.db import Graph
from sqlalchemy.orm.exc import NoResultFound


LOG = getLogger(__name__)


class WeightedControl(Control):
    
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
        if self.__depth and len(state.history) > self.__depth:
            previous = state.history[-self.__depth].local_artist.lastfm_artist
        else:
            previous = None
        for graph in graphs:
            next_weight = graph.weight * unplayed[graph]
            next_weight /= self.__max_weight * max_unplayed
            next_weight **= self.__x_next
            depth_weight = 1
            if previous:
                try:
                    q = state.session.query(Graph.weight)
                    q = q.filter(Graph.from_ == previous)
                    q = q.filter(Graph.to_ == graph.to_)  
                    depth_weight += q.one()[0]
                except NoResultFound:
                    LOG.debug('No link from {0} to {1}.'.format(previous.name, graph.to_.name))
                depth_weight /= self.__max_weight + 1
                depth_weight **= self.__x_depth
            weight = next_weight * depth_weight
            yield (weight, graph.to_)
    
    def select_track(self, state, lastfm_artist):
        tracks = [track 
                  for local_artist in lastfm_artist.local_artists
                  for track in local_artist.tracks
                  if track in state.unplayed_tracks]
        shuffle(tracks)
        track = tracks[0]
        state.unplayed_tracks.remove(track)
        return track
    
    def random_track(self, state):
        return state.unplayed_tracks.pop()

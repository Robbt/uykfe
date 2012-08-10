
from logging import getLogger
from random import choice

from uykfe.sequence.base import State, Control
from uykfe.support.db import LocalTrack


LOG = getLogger(__name__)


class DbState(State):
    
    def __init__(self, session, limit):
        self.__session = session
        all_tracks = list(session.query(LocalTrack).all())
        self.unplayed_tracks = set(all_tracks)
        self.history = []
        self.__limit = limit
        
    @property
    def session(self):
        return self.__session
    
    @property
    def limit(self):
        return self.__limit
    
    def record_track(self, track):
        self.history.append(track)
        
        
class DbControl(Control):
    
    def __init__(self, directed):
        self._directed = directed
        
    def select_track(self, state, lastfm_artist):
        LOG.debug('Selecting for {0}.'.format(lastfm_artist.name))
        def tracks():
            for local_artist in lastfm_artist.local_artists:
                LOG.debug(' {0}:'.format(local_artist.name))
                for track in local_artist.tracks:
                    if track in state.unplayed_tracks:
                        LOG.debug('  {0}/{1}.'.format(track.name, track.url))
                        yield track
        track=choice(list(tracks()))
#        track = choice([track 
#                        for local_artist in lastfm_artist.local_artists
#                        for track in local_artist.tracks
#                        if track in state.unplayed_tracks])
        state.unplayed_tracks.remove(track)
        return track
    
    def random_track(self, state):
        track = choice(list(state.unplayed_tracks))
        state.unplayed_tracks.remove(track)
        state.history = []  # reset
        return track
    
    def weighted_artists(self, state, track):
        artists = set()
        for graph in track.local_artist.lastfm_artist.graph_out[0:state.limit]:
            artists.add(graph.to_)
            LOG.debug('Directed: {0}/{1}.'.format(graph.to_.name, graph.weight))
            yield (graph.weight, graph.to_)
        if not self._directed:
            for graph in track.local_artist.lastfm_artist.graph_in[0:state.limit]:
                LOG.debug('Undirected: {0}/{1}.'.format(graph.from_.name, graph.weight))
                if graph.from_ not in artists:
                    artists.add(graph.from_)
                    yield (graph.weight, graph.from_)

    def _unplayed(self, state, artist):
        unplayed = 0
        for local_artist in artist.local_artists:
            for track in local_artist.tracks:
                if track in state.unplayed_tracks:
                    unplayed += 1
        return unplayed


from random import shuffle

from uykfe.sequence.base import State, Control
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
        

class DbControl(Control):
    
    def weight_options(self, state, graphs):
        for graph in graphs:
            unplayed = 0
            for artist in graph.to_.local_artists:
                for track in artist.tracks:
                    if track in state.unplayed_tracks:
                        unplayed += 1
            yield (graph.weight * unplayed, graph.to_)
        
    
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

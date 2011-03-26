
from random import shuffle
from time import sleep

from uykfe.sequence.base import State, Control
from uykfe.support.db import LocalTrack



class SimpleState(State):
    
    def __init__(self, session, squeeze):
        self.__session = session
        self.__squeeze = squeeze
        all_tracks = list(session.query(LocalTrack).all())
        shuffle(all_tracks)
        self.unplayed_tracks = set(all_tracks)
        
    @property
    def session(self):
        return self.__session
    
    @property
    def current_url(self):
        if self.__squeeze.playlist_remaining:
            return self.__squeeze.url
        else:
            return None
    
    def wait(self):
        while self.__squeeze.playlist_remaining > 1:
            sleep(10)


class SimpleControl(Control):
    
    def weight_options(self, state, graphs):
        for graph in graphs:
            unplayed = 0
            for artist in graph.to_.local_artists:
                for track in artist.tracks:
                    if track not in state.unplayed_tracks:
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

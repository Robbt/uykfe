
from logging import getLogger, basicConfig, DEBUG, INFO
from random import shuffle, random
from time import sleep

from uykfe.support.db import LocalTrack, open_db
from uykfe.support.squeeze import SqueezeServer
from sqlalchemy.orm.exc import NoResultFound


LOG = getLogger(__name__)


def play(session, squeeze):
    unplayed_tracks = list(session.query(LocalTrack).all())
    shuffle(unplayed_tracks)
    unplayed_tracks = set(unplayed_tracks)
    while unplayed_tracks:
        remaining = squeeze.playlist_remaining
        if not remaining:
            LOG.info('No current file.')
            add_unplayed(squeeze, unplayed_tracks)
        elif remaining == 1:
            add_from_graph(session, squeeze, unplayed_tracks)
        sleep(10)
    
        
def add_unplayed(squeeze, unplayed_tracks):
    squeeze.playlist_add(unplayed_tracks.pop().url)
    

def add_from_graph(session, squeeze, unplayed_tracks):
    url = squeeze.url
    try:
        track = session.query(LocalTrack).filter(LocalTrack.url == url).one()
        options = track.local_artist.lastfm_artist.graph_out
        weighted_artists = list(weight_options(options, unplayed_tracks))
        total_weight = sum(map(lambda x: x[0], weighted_artists))
        index = total_weight * random()
        while weighted_artists:
            (weight, artist) = weighted_artists.pop()
            LOG.debug('{0} at {1}: {2}'.format(index, weight, artist.name))
            index -= weight
            if index <= 0:
                add_from_artist(squeeze, artist, unplayed_tracks)
                return
        LOG.error('Weighting failed.')
        exit()
    except NoResultFound:
        LOG.warn('Could not find {0}.'.format(url))
        add_unplayed(squeeze, unplayed_tracks)
        

def weight_options(options, unplayed_tracks):
    for option in options:
        unplayed, total = 0, 0
        for artist in option.to_.local_artists:
            for track in artist.tracks:
                total += 1
                if track not in unplayed_tracks:
                    unplayed += 1
        yield (option.weight * unplayed, option.to_)
        
        
def add_from_artist(squeeze, artist, unplayed_tracks):
    tracks = [track 
              for local_artist in artist.local_artists
              for track in local_artist.tracks
              if track in unplayed_tracks]
    shuffle(tracks)
    track = tracks[0]
    unplayed_tracks.remove(track)
    squeeze.playlist_add(track.url)
    

if __name__ == '__main__':
    basicConfig(level=DEBUG)
    play(open_db()(), SqueezeServer())

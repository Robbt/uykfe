
from collections import defaultdict
from difflib import get_close_matches
from logging import getLogger
from random import shuffle

from uykfe.support.db import open_db, LocalArtist, LastFmArtist
from uykfe.support.config import lastfm_kargs
from uykfe.support.lastfm import LastFm, NotFoundError
from sqlalchemy.orm.exc import NoResultFound


LOG = getLogger(__name__)


def identify_artists(dir=None, name=None):
    session = open_db(dir=dir, name=name)()
    lastfm = LastFm(**lastfm_kargs(dir=dir, name=name))
    for artist in session.query(LocalArtist).filter(LocalArtist.lastfm_artist == None).all():
        name = identify_artist(session, lastfm, artist)
        LOG.info('Identified {0} as {1}.'.format(artist.name, name))
        try:
            lastfm_artist = session.query(LastFmArtist).filter(LastFmArtist.name == name).one()
        except NoResultFound:
            lastfm_artist = LastFmArtist(name=name)
        session.add(lastfm_artist)
        artist.lastfm_artist = lastfm_artist
        session.commit()

        
def identify_artist(session, lastfm, artist):
    
    # first, try scoring from random tracks
    tracks = list(artist.tracks)
    shuffle(tracks)
    score = defaultdict(lambda: 0)
    similar = make_similar(artist.name)
    for track in tracks:
        try:
            weight = 1
            for candidate in similar(lastfm.artists_for_track(track.name)):
                LOG.debug('Track {0} by {1}.'.format(track.name, candidate))
                score[candidate] += weight
                weight = 0.9 * weight
            scores = sorted(score.items(), key=lambda item: item[1], reverse=True)
            if scores and \
                    ((len(scores) == 1 and scores[0][1] > 1) or
                     len(scores) > 1 and scores[0][1] > scores[1][1] * 1.5):
                return scores[0][0]
        except NotFoundError:
            pass
        
    # if we run out of tracks, relax the conditions on the scores
    scores = sorted(score.items(), key=lambda item: item[1], reverse=True)
    if len(scores) == 1 or (len(scores) > 1 and scores[0][1] > scores[1][1]):
        return scores[0][0]
    
    # if we don't have a good score, get closest match
    artists = [score[0] for score in scores]
    close = get_close_matches(artist.name, artists)
    if close:
        return close[0]
    
    # if no match hope that last fm can identify the name
    return lastfm.artist_for_artist(artist.name)
    

def make_similar(artist):
    def similar(artists):
        close = get_close_matches(artist, set(artists))
        if close:
            return close
        else:
            return artists
    return similar


if __name__ == '__main__':
    identify_artists()
    

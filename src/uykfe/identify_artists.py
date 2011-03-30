
from collections import defaultdict
from difflib import get_close_matches
from logging import getLogger, basicConfig, INFO, DEBUG
from random import shuffle

from uykfe.support.db import open_db, LocalArtist, LastFmArtist
from uykfe.support.config import lastfm_kargs
from uykfe.support.lastfm import LastFm, NotFoundError
from sqlalchemy.orm.exc import NoResultFound


LOG = getLogger(__name__)


def identify_artists(dir=None, name=None):
    LOG.info('Opening database.')
    session = open_db(dir=dir, name=name)()
    try:
        lastfm = LastFm(**lastfm_kargs(dir=dir, name=name))
        artists = session.query(LocalArtist).filter(LocalArtist.lastfm_artist == None).all()
        LOG.info('Read {0} artists.'.format(len(artists)))
        for artist in artists:
            name = identify_artist(session, lastfm, artist)
            LOG.info('Identified {0} as {1}.'.format(artist.name, name))
            try:
                lastfm_artist = session.query(LastFmArtist).filter(LastFmArtist.name == name).one()
            except NoResultFound:
                lastfm_artist = LastFmArtist(name=name)
                session.add(lastfm_artist)
            artist.lastfm_artist = lastfm_artist
            session.commit()
    finally:
        session.close()

        
def identify_artist(session, lastfm, artist):
    
    # first, try scoring from random tracks
    LOG.info('Artist {0}.'.format(artist.name))
    tracks = list(artist.tracks)
    shuffle(tracks)
    score = defaultdict(lambda: 0)
    try:
        weight = 2
        for candidate in lastfm.artists_for_artist(artist.name):
            score[candidate] = weight
            LOG.debug(' {0} ({1:4.2f}).'.format(candidate, weight))
            weight = weight * 0.9
    except NotFoundError:
        LOG.warn('Search failed for {0}.'.format(artist.name))
    similar = make_similar(artist.name)
    for track in tracks:
        try:
            weight = 1
            LOG.info(' Track {0}.'.format(track.name))
            for candidate in similar(lastfm.artists_for_track(track.name)):
                LOG.debug('  {0} ({1:4.2f}).'.format(candidate, weight))
                score[candidate] += weight
                weight = 0.9 * weight
            scores = sorted(score.items(), key=lambda item: item[1], reverse=True)
            LOG.debug(str(scores))
            if (len(scores) == 1 and  scores[0][1] > 3) or \
                    (len(scores) > 1 and scores[0][1] > scores[1][1] * 1.5) or \
                    (len(scores) > 1 and scores[0][1] > 5 and scores[0][1] > scores[1][1]):
                return scores[0][0]
        except NotFoundError:
            pass
    
    if score:
        scores = sorted(score.items(), key=lambda item: item[1], reverse=True)
        LOG.warn('Using poor match')
        return scores[0][0]
    
    LOG.warn('Using original name')
    return artist.name


def make_similar(artist):
    def unique(artists):
        known = set()
        for artist in artists:
            if artist not in known:
                yield artist
                known.add(artist)
    def similar(artists):
        # filter, but keep order
        artists = list(unique(artists))
        close = set(get_close_matches(artist, artists, cutoff=0.5))
        if not close:
            close = set(artists)
        for candidate in artists:
            if candidate in close:
                yield candidate
    return similar


if __name__ == '__main__':
    basicConfig(level=INFO)
    identify_artists()
    

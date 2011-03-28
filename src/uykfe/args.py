
from argparse import ArgumentError, ArgumentParser
from random import choice
from logging import getLogger, basicConfig, DEBUG, INFO

from uykfe.support.db import LocalTrack, LocalArtist


LOG = getLogger(__name__)


def positive_int(value):
    try:
        nzi = int(value)
        if nzi < 0:
            raise ArgumentError('{0} is negative.'.format(value))
        else:
            return nzi
    except:
        raise ArgumentError('{0} is not an integer.'.format(value))
    
    
def build_weighted_parser(description):
    parser = ArgumentParser(description=description)
    parser.add_argument('-x', '--localexp', default=1, type=float, help='exponent for local weight')
    parser.add_argument('-v', '--debug', default=False, action='store_true', help='debug logging')
    parser.add_argument('-l', '--limit', default=None, type=positive_int, help='limit to top LIMIT edges')
    return parser


def add_inital_artist(parser):
    parser.add_argument('-a', '--artist', help='starting artist')
    parser.add_argument('-t', '--track', help='starting track')
    
    
def add_depth(parser):
    parser.add_argument('-o', '--unidirectional', default=False, action='store_true', help='directed graph')
    parser.add_argument('-d', '--depth', default=0, type=positive_int, help='depth for delayed weighting')
    parser.add_argument('-y', '--depthexp', default=1, type=float, help='exponent for depth weight')
    
    
def set_logging(debug):
    if debug:
        basicConfig(level=DEBUG)
    else:
        basicConfig(level=INFO)


def find_track(session, artist, title):
    if not (artist or title):
        return None
    q = session.query(LocalTrack)
    if title:
        q = q.filter(LocalTrack.name.contains(title))
    if artist:
        q = q.join(LocalArtist).filter(LocalArtist.name.contains(artist))
    tracks = q.all()
    if not tracks:
        raise Exception('No match found for {0} by {1}.'.format(title, artist))
    artists = set(track.local_artist.lastfm_artist 
                  for track in tracks)
    if len(artists) > 1:
        raise Exception('Found multiple artists: {0}.'.format(', '.join(artist.name for artist in artists)))
    track = choice(tracks)
    LOG.info('Context track {0} by {1}.'.format(track.name, track.local_artist.name))
    return track

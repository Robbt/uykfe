
from itertools import islice
from logging import getLogger, basicConfig, DEBUG, INFO
from argparse import ArgumentParser, ArgumentError
from random import choice

from uykfe.support.db import open_db, LocalArtist, LocalTrack
from uykfe.sequence.base import sequence
from uykfe.sequence.static import StaticState
from uykfe.sequence.weighted.weighted import WeightedControl


LOG = getLogger(__name__)


def non_zero_int(value):
    try:
        nzi = int(value)
        if nzi < 0:
            raise ArgumentError('{0} is negative.'.format(value))
        else:
            return nzi
    except:
        raise ArgumentError('{0} is not an integer.'.format(value))


def build_parser():
    parser = ArgumentParser(description='Print a playlist to stdout')
    parser.add_argument('count', metavar='N', type=int,
                        help='the number of entries')
    parser.add_argument('-a', '--artist', help='starting artist')
    parser.add_argument('-t', '--track', help='starting track')
    parser.add_argument('-d', '--depth', default=0, type=non_zero_int, help='depth for delayed weighting')
    parser.add_argument('-x', '--localexp', default=1, type=int, help='exponent for local weight')
    parser.add_argument('-y', '--depthexp', default=1, type=int, help='exponent for depth weight')
    return parser


def find_track(session, artist, title):
    if not (artist or title):
        return None
    q = session.query(LocalTrack)
    if title:
        q = q.filter(LocalTrack.name.contains(title))
    if artist:
        q = q.join(LocalArtist).filter(LocalArtist.name.contains(artist))
    tracks = q.all()
    if tracks:
        track = choice(tracks)
        LOG.info('Using context track {0} by {1}.'.format(track.name, track.local_artist.name))
        return track
    else:
        raise Exception('No match found for {0} by {1}.'.format(title, artist))


if __name__ == '__main__':
    basicConfig(level=DEBUG)
    parser = build_parser()
    args = parser.parse_args()
    session = open_db()()
    track = find_track(session, args.artist, args.track)
    state = StaticState(session)
    if track:
        state.record_track(track)
    control = WeightedControl(state, args.localexp, args.depth, args.depthexp)
    for track in islice(sequence(state, control), args.count):
        print(track.url)

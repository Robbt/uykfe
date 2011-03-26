
from itertools import islice
from logging import getLogger, basicConfig, DEBUG, INFO
from argparse import ArgumentParser

from uykfe.support.db import open_db, LastFmArtist, LocalArtist, LocalTrack
from uykfe.sequence.base import sequence
from uykfe.sequence.static import StaticState, StaticControl


LOG = getLogger(__name__)


def build_parser():
    parser = ArgumentParser(description='Print a playlist to stdout')
    parser.add_argument('count', metavar='N', type=int,
                        help='the number of entries')
    parser.add_argument('-a', '--artist', help='starting artist')
    parser.add_argument('-t', '--track', help='starting track')
    return parser


def find_track(session, artist, title):
    if not (artist or title):
        return None
    q = session.query(LastFmArtist).join(LocalArtist)
    if artist:
        q = q.filter(LocalArtist.name.contains(artist))
    if title:
        q = q.join(LocalTrack).filter(LocalTrack.name.contains(title))
    return q.one()


if __name__ == '__main__':
    #basicConfig(level=INFO)
    parser = build_parser()
    args = parser.parse_args()
    session = open_db()()
    track = find_track(session, args.artist, args.track)
    state = StaticState(session)
    state.current_url = track.url if track else None
    control = StaticControl()
    for track in islice(sequence(state, control), args.count):
        print(track.url)
        
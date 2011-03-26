
from itertools import islice
from logging import getLogger, basicConfig, DEBUG, INFO
from random import choice

from uykfe.support.db import open_db, LocalArtist, LocalTrack
from uykfe.sequence.base import sequence
from uykfe.sequence.static import StaticState
from uykfe.sequence.weighted.weighted import WeightedControl
from uykfe.args import build_weighted_parser


LOG = getLogger(__name__)


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
    basicConfig(level=INFO)
    parser = build_weighted_parser('Print a playlist to stdout')
    parser.add_argument('count', metavar='N', type=int, help='the number of entries')
    args = parser.parse_args()
    session = open_db(name=args.config)()
    track = find_track(session, args.artist, args.track)
    state = StaticState(session)
    if track:
        state.record_track(track)
    control = WeightedControl(state, args.localexp, args.depth, args.depthexp)
    for track in islice(sequence(state, control), args.count):
        print(track.url)

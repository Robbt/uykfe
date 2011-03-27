
from itertools import islice
from logging import basicConfig, DEBUG, INFO

from uykfe.support.db import open_db
from uykfe.sequence.base import sequence
from uykfe.sequence.static import StaticState
from uykfe.sequence.weighted.weighted import WeightedControl
from uykfe.args import build_weighted_parser, find_track, add_depth,\
    add_inital_artist, set_logging


if __name__ == '__main__':
    parser = build_weighted_parser('Print a playlist to stdout')
    add_depth(parser)
    add_inital_artist(parser)
    parser.add_argument('count', metavar='N', type=int, help='the number of entries')
    args = parser.parse_args()
    set_logging(args.debug)
    session = open_db()()
    track = find_track(session, args.artist, args.track)
    state = StaticState(session)
    if track:
        state.record_track(track)
    control = WeightedControl(state, args.localexp, args.depth, args.depthexp)
    for track in islice(sequence(state, control), args.count):
        print(track.url)

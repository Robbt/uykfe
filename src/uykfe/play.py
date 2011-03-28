
from uykfe.support.db import open_db
from uykfe.support.squeeze import SqueezeServer
from uykfe.sequence.base import sequence
from uykfe.sequence.squeeze import SqueezeState
from uykfe.args import build_weighted_parser, add_depth, set_logging
from uykfe.sequence.weighted.weighted import WeightedControl


if __name__ == '__main__':
    parser = build_weighted_parser('Add items to SqueezeCenter playlist as needed')
    add_depth(parser)
    parser.add_argument('-c', '--config', default='.uykferc', help='config file')
    args = parser.parse_args()
    set_logging(args.debug)
    squeeze = SqueezeServer(name=args.config)
    state = SqueezeState(open_db()(), args.limit, squeeze)
    control = WeightedControl(state, args.localexp, args.depth, args.depthexp, args.unidirectional)
    state.wait()
    for track in sequence(state, control):
        squeeze.playlist_add(track.url)
        state.wait()


from logging import getLogger, basicConfig, DEBUG, INFO

from uykfe.support.db import open_db
from uykfe.support.squeeze import SqueezeServer
from uykfe.sequence.base import sequence
from uykfe.sequence.squeeze import SqueezeState
from uykfe.args import build_weighted_parser
from uykfe.sequence.weighted.weighted import WeightedControl


LOG = getLogger(__name__)


if __name__ == '__main__':
    basicConfig(level=INFO)
    parser = build_weighted_parser('Add items to SqueezeCenter playlist as needed')
    parser.add_argument('-c', '--config', default='.uykferc', help='config file')
    args = parser.parse_args()
    squeeze = SqueezeServer(name=args.config)
    state = SqueezeState(open_db()(), squeeze)
    control = WeightedControl(state, args.localexp, args.depth, args.depthexp)
    state.wait()
    for track in sequence(state, control):
        squeeze.playlist_add(track.url)
        state.wait()

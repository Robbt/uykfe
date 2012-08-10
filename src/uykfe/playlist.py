
from logging import getLogger
from sys import getfilesystemencoding, stdout
from itertools import islice

from uykfe.support.db import open_db
from uykfe.sequence.base import sequence
from uykfe.args import build_weighted_parser, find_track, add_depth,\
    add_inital_artist, set_logging
from uykfe.sequence.distance.distance import DistanceControl, DistanceState


LOG = getLogger(__name__)


if __name__ == '__main__':
    parser = build_weighted_parser('Print a playlist to stdout')
    add_depth(parser)
    add_inital_artist(parser)
    parser.add_argument('count', metavar='N', type=int, help='the number of entries')
    args = parser.parse_args()
    set_logging(args.debug)
    LOG.info('File system encoding {0}'.format(getfilesystemencoding()))
    LOG.info('Stdout encoding {0}'.format(stdout.encoding))
    session = open_db()()
    track = find_track(session, args.artist, args.track)
    state = DistanceState(session, args.limit, args.unidirectional)
    if track:
        state.record_track(track)
    control = DistanceControl(state, args.localexp, args.depth, args.depthexp, args.unidirectional, args.neighbour)
    stdout.buffer.write('#EXTM3U\n'.encode('utf8'))
    for track in islice(sequence(state, control), args.count):
        url = track.url
        if url.startswith('file://'):
            url = url[len('file://'):]
#        LOG.info(url)
#        print(url)
        stdout.buffer.write((url + '\n').encode('utf8'))



from logging import getLogger, basicConfig, DEBUG, INFO

from uykfe.support.db import open_db
from uykfe.support.squeeze import SqueezeServer
from uykfe.sequence.simple import SimpleState, SimpleControl
from uykfe.sequence.base import sequence


LOG = getLogger(__name__)


if __name__ == '__main__':
    basicConfig(level=DEBUG)
    squeeze = SqueezeServer()
    state = SimpleState(open_db()(), squeeze)
    control = SimpleControl()
    for track in sequence(state, control):
        squeeze.playlist_add(track.url)
        state.wait()

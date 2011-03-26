
from logging import getLogger, basicConfig, DEBUG, INFO

from uykfe.support.db import open_db
from uykfe.support.squeeze import SqueezeServer
from uykfe.sequence.base import sequence
from uykfe.sequence.db import DbControl
from uykfe.sequence.squeeze import SqueezeState


LOG = getLogger(__name__)


if __name__ == '__main__':
    basicConfig(level=INFO)
    squeeze = SqueezeServer()
    state = SqueezeState(open_db()(), squeeze)
    control = DbControl()
    state.wait()
    for track in sequence(state, control):
        squeeze.playlist_add(track.url)
        state.wait()

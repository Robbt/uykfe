
from uykfe.sequence.db import DbControl


class SimpleControl(DbControl):
    
    def weighted_artists(self, state, track):
        for (weight, artist) in super(SimpleControl, self).weighted_artists(state, track):
            yield (weight * self._unplayed(state, artist), artist)

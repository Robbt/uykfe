
from uykfe.sequence.db import DbState


class StaticState(DbState):
    
    @property
    def current_url(self):
        if self.history:
            return self.history[-1]
        else:
            return None

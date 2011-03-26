
from uykfe.sequence.db import DbControl


class SimpleControl(DbControl):
    
    def weight_options(self, state, graphs):
        for graph in graphs:
            unplayed = 0
            for artist in graph.to_.local_artists:
                for track in artist.tracks:
                    if track in state.unplayed_tracks:
                        unplayed += 1
            yield (graph.weight * unplayed, graph.to_)
        
    

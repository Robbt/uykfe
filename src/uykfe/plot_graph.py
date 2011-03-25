
from logging import getLogger 

from altgraph.Graph import Graph

from uykfe.support.db import LastFmArtist, open_db
from altgraph.Dot import Dot


LOG = getLogger(__name__)


def copy_to_graph(session):
    graph = Graph()
    count = 0
    for artist in session.query(LastFmArtist).all():
        graph.add_node(artist.id, artist)
        for edge in artist.graph_out:
            target = edge.to_
            graph.add_node(target.id, target)
            graph.add_edge(artist.id, target.id, edge, create_nodes=False)
        if not count % 100:
            LOG.info('Added {0} nodes.'.format(count))
        count += 1
    return graph


def write_graph(graph):
    dot = Dot(graph)
    dot.display()
    
    
if __name__ == '__main__':
    write_graph(copy_to_graph(open_db()()))

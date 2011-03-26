
from logging import getLogger 
from unicodedata import normalize, category

from altgraph.Graph import Graph
from altgraph.Dot import Dot

from uykfe.support.db import LastFmArtist, open_db


LOG = getLogger(__name__)


def copy_to_graph(session):
    graph = Graph()
    count = 0
    for artist in session.query(LastFmArtist).all():
        if artist.graph_out:
            graph.add_node(artist.id, artist)
            edges = list(artist.graph_out)
            edges.sort(key=lambda e: e.weight, reverse=True)
            for edge in edges[0:2]:
                target = edge.to_
                graph.add_node(target.id, target)
                graph.add_edge(artist.id, target.id, edge, create_nodes=False)
            if not count % 100:
                LOG.info('Added {0} nodes.'.format(count))
            count += 1
        else:
            LOG.warn('Discarding unconnected {0}.'.format(artist.name))
    return graph


def write_graph(graph):
    dot = Dot(graph)
    dot.style(size='100000,10000')
    for node in graph:
        (_, artist, _, _) = graph.describe_node(node)
        #name = ''.join((c for c in normalize('NFD', artist.name) if category(c) != 'Mn' and c != '"'))
        name = ''.join(c for c in artist.name if c != '"')
        dot.node_style(node, label=name)
    dot.display()
    
    
if __name__ == '__main__':
    write_graph(copy_to_graph(open_db()()))


from collections import defaultdict
from logging import basicConfig, DEBUG, INFO, getLogger
from argparse import ArgumentError
from bisect import bisect_left

from networkx import DiGraph
#from networkx.readwrite.graphml import write_graphml
from networkx.readwrite.gexf import write_gexf
from sqlalchemy.sql.functions import max as max_, count

from uykfe.support.db import open_db, LastFmArtist, Graph
from uykfe.sequence.static import StaticState
from uykfe.args import build_weighted_parser, find_track, add_inital_artist,\
    positive_int, set_logging
from uykfe.sequence.weighted.weighted import normalize
from sqlalchemy.sql.expression import and_


LOG = getLogger(__name__)


def collect(session, zero):
    max_weight = session.query(max_(Graph.weight)).one()[0]
    zero *= max_weight
    LOG.info('Collecting all nodes, edges with weights over {0:7.1f} (max {1:7.1f}).'.format(zero, max_weight))
    edges =  set(session.query(Graph).filter(Graph.weight > zero).all())
    nodes = set(edge.from_ for edge in edges)
    nodes.update(edge.to_ for edge in edges)
    LOG.info('Collected {0}/{1} nodes and {2}/{3} edges.'.format(
            len(nodes), session.query(LastFmArtist).count(), 
            len(edges), session.query(Graph).count()))
    return (nodes, edges, zero)


def restrict(nodes_in, edges_map, artist):
    # TODO - add zero
    LOG.info('Restricting to graph reachable from {0}.'.format(artist.name))
    stack, nodes, edges = [artist], set(), set()
    while stack:
        node = stack.pop()
        if node not in nodes and node in nodes_in:
            nodes.add(node)
            for edge in node.graph_out:
                if edge in edges_map:
                    edges.add(edges_map[edge])
                    stack.append(edge.to_)
    LOG.info('Restricted to {0} nodes and {1} edges.'.format(len(nodes), len(edges)))
    return (nodes, edges)


def filter(nodes_in, edges_in, exponent, min_, limit, session, zero):
    LOG.info('Weighting with exponent {0:3.1f}.'.format(exponent))
    if limit:
        LOG.info('Restricting to top {0} edges.'.format(limit))
    if min_:
        LOG.info('Nodes must have at least {0} outgoing edges.'.format(min_))
    nodes, weighted_edges = set(), set()
    max_weight = max(edge.weight for edge in edges_in)
    for node in nodes_in:
        weighted = [(normalize(edge.weight, exponent, max_weight), edge) 
                    for edge in session.query(Graph).filter(and_(Graph.from_id == node.id, Graph.weight > zero))]
        if limit and limit < len(weighted):
            weighted.sort(key=lambda we: we[0], reverse=True)
            weighted = weighted[0:limit]
        weighted_edges.update(weighted)
        nodes.add(node)
    if min_:
        LOG.info('Discarding nodes with fewer than {0} outward links.'.format(min_))
        # repeat filtering to drop edges without nodes
        changed = True
        while changed:
            len_edges, len_nodes = len(weighted_edges), len(nodes)
            LOG.info('Iterating to with {0} nodes, {1} edges.'.format(len_nodes, len_edges))
            weighted_edges = set((weight, edge) for (weight, edge) in weighted_edges
                                 if edge.from_ in nodes and edge.to_ in nodes)
            count = defaultdict(lambda: 0)
            for (_, edge) in weighted_edges:
                count[edge.from_] += 1
            nodes = set(node for node in count.keys() if count[node] >= min_)
            changed = len_edges != len(weighted_edges) or len_nodes != len(nodes)
    LOG.info('Filtered {0} nodes and {1} edges.'.format(len(nodes), len(weighted_edges)))
    return (nodes, weighted_edges)


def flatten(weights_map):
    weights = list(weights_map.keys())
    weights.sort()
    def remap(weight):
        return (bisect_left(weights, weight) / len(weights))
    flattened = dict((weight, remap(weight)) for weight in weights)
    log_range('Flattened weight', flattened.values())
    return flattened


def rgb(value, white, black):
    value = 1 - value # black is highest
    byte = black + int((white - black) * value)
    byte = min(255, max(0, byte))
    return {'color': {'r': byte, 'g': byte, 'b': byte}}


def log_range(name, values):
    values = list(values)
    values.sort()
    LOG.info('{0} range: {1:4.2f} to {2:4.2f}.'.format(name, values[0], values[-1]))
    LOG.info('{0} quartiles: {1:4.2f} {2:4.2f} {3:4.2f}.'.format(name,
        values[int(len(values)/4)],
        values[int(2 * len(values)/4)],
        values[int(3 * len(values)/4)]))
    return (values[0], values[-1])


def dump(nodes, weighted_edges, white, black, flatten_colours, flatten_weights):
    graph = DiGraph()
    for node in nodes:
        graph.add_node(node.id, label=node.name)
    (min_weight, max_weight) = log_range('Weight', map(lambda we: we[0], weighted_edges))
    if flatten_colours or flatten_weights:
        flattened_weights = flatten(dict((weight, weight) for (weight, edge) in weighted_edges))
    for (weight, edge) in weighted_edges:
        colour = flattened_weights[weight] if flatten_colours else (weight - min_weight) / (max_weight - min_weight)
        weight = flattened_weights[weight] if flatten_weights else weight
        graph.add_edge(edge.from_.id, edge.to_.id, 
                       weight=weight, 
                       viz=rgb(colour, white, black))
    #write_graphml(graph, 'uykfe.graphml')
    write_gexf(graph, 'uykfe.gexf')
    # fix namespace bug
    with open('uykfe.gexf') as input:
        xml = input.read()
    xml = xml.replace('xmlns:viz="http://www.gexf.net/1.1draft/viz" ', '', 1)
    with open('uykfe.gexf', 'w') as output:
        xml = output.write(xml)
    

def level(value):
    try:
        grey = int(value)
        if grey < 0:
            raise ArgumentError('{0} is negative.'.format(value))
        elif grey > 255:
            raise ArgumentError('{0} is over 255.'.format(value))
        else:
            return grey
    except:
        raise ArgumentError('{0} is not an integer.'.format(value))
    
    
if __name__ == '__main__':
    parser = build_weighted_parser('Dump graph to file')
    add_inital_artist(parser)
    parser.add_argument('-n', '--min', default=0, type=positive_int, help='minimum number of edges')
    parser.add_argument('-w', '--white', default=255, type=level, help='white level')
    parser.add_argument('-b', '--black', default=0, type=level, help='black level')
    parser.add_argument('-f', '--flatten', default=False, action='store_true', help='flatten edge colours?')
    parser.add_argument('-g', '--weights', default=False, action='store_true', help='flatten weights?')
    parser.add_argument('-z', '--zero', default=0, type=float, help='fractional lower limit for weights')
    args = parser.parse_args()
    set_logging(args.debug)
    session = open_db()()
    artist, track = None, find_track(session, args.artist, args.track)
    if track:
        artist = track.local_artist.lastfm_artist
    state = StaticState(session, args.limit)
    (nodes, edges, zero) = collect(session, args.zero)
    if artist:
        (nodes, edges) = restrict(nodes, dict((edge, edge) for edge in edges), artist)
    (nodes, weighted_edges) = filter(nodes, edges, args.localexp, args.min, args.limit, session, zero)
    if artist:
        (nodes, weighted_edges) = restrict(nodes, dict((edge, (weight, edge)) for (weight, edge) in weighted_edges), artist)
    dump(nodes, weighted_edges, args.white, args.black, args.flatten, args.weights)
    
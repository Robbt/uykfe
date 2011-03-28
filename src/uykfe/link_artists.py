
from argparse import ArgumentParser
from collections import defaultdict
from logging import getLogger, basicConfig, INFO
from random import randint

from sqlalchemy.sql.expression import text, and_

from uykfe.support.db import open_db, LastFmArtist, Graph
from uykfe.args import positive_int


LOG = getLogger(__name__)


def link_artists(upper, lower, session):
    try:
        for artist in session.query(LastFmArtist).filter(LastFmArtist.linked == False).all():
            link_artist(session, artist, upper)
        trim_links(session, lower)
    finally:
        session.close()
        
        
def trim_links(session, lower):
    by_incoming = defaultdict(lambda: [])
    for artist in session.query(LastFmArtist).all():
        by_incoming[len(artist.graph_in)].append(artist)
    while True:
        keys = list(by_incoming.keys())
        keys.sort(reverse=True)
        upper = keys[0]
        if upper <= lower: return
        artists = by_incoming[upper]
        artist = artists.pop(randint(0, len(artists)-1))
        if trim_artist(session, artist, lower):
            by_incoming[upper-1].append(artist)
        if not artists:
            del by_incoming[upper]
            
            
def trim_artist(session, artist, lower):
    # we need to reduce the links coming in to this node, so we select the incoming
    # artist who (1) has the most links out and (2) has the lowest scoring link
    # (but without lowering to less than lower).
    n_in = len(artist.graph_in)
    ids = session.execute(text('''
select from_id, to_id
  from (select g1.from_id as from_id,
               g1.to_id as to_id,
               count(g2.from_id) as n_out, 
               g1.weight as weight
          from lastfm_artists as a,
               graph as g1,
               graph as g2
         where a.id = g1.from_id
               and a.id = g2.from_id
           and :id = g1.to_id
         group by a.id
         order by n_out desc, weight asc)
 where n_out > :lower
 limit 1
'''), params={'id': artist.id, 'lower': lower}).first()
    if not ids: return False
    graph = session.query(Graph).filter(and_(Graph.from_id == ids['from_id'], 
                                             Graph.to_id == ids['to_id'])).one()
    LOG.info('Trimming {0} from {1} via {2}/{3}.'.format(artist.name, n_in, graph.from_, graph.weight))
    assert graph in artist.graph_in, graph
    session.delete(graph)
    session.commit()
    assert n_in == len(artist.graph_in) + 1, (n_in, len(artist.graph_in))  # check deletion is propagated
    return True


#def link_artist(session, artist):
#    session.execute(text('''
#insert 
#  into graph (from_id, to_id, weight)
#select *
#  from (select :id as from_id,
#               a.id as to_id,
#               sum(min(w1.weight, w2.weight)) as weight
#          from lastfm_artists as a,
#               lastfm_tagweights as w2,
#               (select w.weight, w.lastfm_tagword_id
#                  from lastfm_tagweights as w
#                 where lastfm_artist_id == :id) as w1
#         where w2.lastfm_tagword_id == w1.lastfm_tagword_id
#           and w2.lastfm_artist_id == a.id
#           and a.id != :id
#         group by a.name
#         order by weight desc)
# where weight > 1;
#'''), params={'id': artist.id})
#    artist.linked = True
#    session.commit()
#    LOG.info('Linked {0}'.format(artist.name))


def link_artist(session, artist, limit):
    session.execute(text('''
insert 
  into graph (from_id, to_id, weight)
select :id as from_id,
       a.id as to_id,
       sum(w1.weight * w2.weight) as weight
  from lastfm_artists as a,
       lastfm_tagweights as w2,
       (select w.weight, w.lastfm_tagword_id
          from lastfm_tagweights as w
         where lastfm_artist_id == :id) as w1
 where w2.lastfm_tagword_id == w1.lastfm_tagword_id
   and w2.lastfm_artist_id == a.id
   and a.id != :id
 group by a.name
 order by weight desc
 limit :limit'''), params={'id': artist.id, 'limit': limit})
    artist.linked = True
    session.commit()
    LOG.info('Linked {0}'.format(artist.name))
    

#def link_artist(session, artist):
#    session.execute(text('''
#insert 
#  into graph (from_id, to_id, weight)
#select :id as from_id,
#       a.id as to_id,
#       sum(w1.weight * w2.weight) as weight
#  from lastfm_artists as a,
#       lastfm_tagweights as w2,
#       (select w.weight, w.lastfm_tagword_id
#          from lastfm_tagweights as w
#         where lastfm_artist_id == :id) as w1
# where w2.lastfm_tagword_id == w1.lastfm_tagword_id
#   and w2.lastfm_artist_id == a.id
#   and a.id != :id
# group by a.name
# order by weight desc'''), params={'id': artist.id})
#    artist.linked = True
#    session.commit()
#    LOG.info('Linked {0}'.format(artist.name))
    

#def link_artist(session, artist):
#    session.execute(text('''
#insert 
#  into graph (from_id, to_id, weight)
#select *
#  from (select :id as from_id,
#               a.id as to_id,
#               count(*) as weight
#          from lastfm_artists as a,
#               lastfm_tagweights as w2,
#               (select w.weight, w.lastfm_tagword_id
#                  from lastfm_tagweights as w
#                 where lastfm_artist_id == :id) as w:id
#         where w2.lastfm_tagword_id == w:id.lastfm_tagword_id
#           and w2.lastfm_artist_id == a.id
#           and a.id != :id
#         group by a.name
#         order by weight desc)
# where weight > 1'''), params={'id': artist.id})
#    artist.linked = True
#    session.commit()
#    LOG.info('Linked {0}'.format(artist.name))
    

if __name__ == '__main__':
    basicConfig(level=INFO)
    parser = ArgumentParser('Link related artists in the database')
    parser.add_argument('-u', '--upper', default=6, type=positive_int, help='initial number of edges')
    parser.add_argument('-l', '--lower', default=3, type=positive_int, help='final number of edges')
    args = parser.parse_args()
    link_artists(args.upper, args.lower, open_db()())

    


from logging import getLogger, basicConfig, INFO
from argparse import ArgumentParser

from sqlalchemy.sql.expression import text

from uykfe.support.db import open_db, LastFmArtist
from uykfe.args import positive_int


LOG = getLogger(__name__)


def link_artists(upper, lower, session):
    try:
        for artist in session.query(LastFmArtist).filter(LastFmArtist.linked == False).all():
            link_artist(session, artist, upper)
        trim_links(session, lower)
    finally:
        session.close()
        

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

    

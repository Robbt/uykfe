
from logging import getLogger, basicConfig, INFO

from uykfe.support.db import open_db, LastFmArtist
from sqlalchemy.sql.expression import text


LOG = getLogger(__name__)


def link_artists(dir=None, name=None):
    session = open_db(dir=dir, name=name)()
    try:
        for artist in session.query(LastFmArtist).filter(LastFmArtist.linked == False).all():
            link_artist(session, artist)
    finally:
        session.close()
        

def link_artist(session, artist):
    session.execute(text('''
insert 
  into graph (from_id, to_id, weight)
select :id as from_id,
       a.id as to_id,
       sum(w1.weight*w2.weight) as weight
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
 limit 10'''), params={'id': artist.id})
    artist.linked = True
    session.commit()
    LOG.info('Linked {0}'.format(artist.name))
    

if __name__ == '__main__':
    basicConfig(level=INFO)
    link_artists()
    

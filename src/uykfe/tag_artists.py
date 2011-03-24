
from logging import getLogger

from uykfe.support.db import open_db, LastFmArtist, LastFmTagWord,\
    LastFmTagWeight
from uykfe.support.config import lastfm_kargs
from uykfe.support.lastfm import LastFm, NotFoundError
from sqlalchemy.orm.exc import NoResultFound


LOG = getLogger(__name__)


def tag_artists(dir=None, name=None):
    session = open_db(dir=dir, name=name)()
    lastfm = LastFm(**lastfm_kargs(dir=dir, name=name))
    for artist in session.query(LastFmArtist).filter(LastFmArtist.tagged == False).all():
        tag_artist(session, lastfm, artist)
        

def tag_artist(session, last_fm, artist):
    try:
        for (tag, weight) in last_fm.tags_for_artist(artist.name):
            try:
                word = session.query(LastFmTagWord).filter(LastFmTagWord.word == tag).one()
            except NoResultFound:
                word = LastFmTagWord(tag)
                session.add(word)
            session.add(LastFmTagWeight(weight, word, artist))
    except NotFoundError:
        pass
    artist.tagged = True
    session.commit()
    

if __name__ == '__main__':
    tag_artists()
    


from logging import getLogger, basicConfig, INFO, DEBUG
from os import walk
from os.path import join
from urllib.parse import urlunparse

from stagger import read_tag
from sqlalchemy.orm.exc import NoResultFound

from uykfe.support.config import mp3_dirs
from uykfe.support.db import open_db, LocalTrack, LocalArtist
from stagger.errors import NoTagError


LOG = getLogger(__name__)


def scan_config():
    session = open_db()()
    try:
        scan_dirs(session, mp3_dirs())
    finally:
        session.close()
    
    
def scan_dirs(session, directories):
    LOG.debug('Retrieving all known tracks from database.')
    not_found = {} # map from url to instance
    for track in session.query(LocalTrack).all():
        not_found[track.url] = track
    LOG.debug('Retrieved.')
    count = 0
    for dir in directories:
        for root, _, files in walk(dir):
            for file in files:
                if file.lower().endswith('.mp3'):
                    path = join(root, file)
                    scan_path(session, not_found, path)
                    if not count % 100:
                        LOG.info('Scanned {0} tracks.'.format(count))
                    count += 1
    if not_found:
        LOG.info('Removing {0} tracks from database.'.format(len(not_found)))
        for track in not_found.values():
            session.delete(track)
    # TODO - clean out unused local artists
 
                    
def scan_path(session, not_found, path):
    url = urlunparse(('file', '', path, '', '', ''))
    if url in not_found:
        del not_found[url]
        return
    LOG.debug('Scanning {0}.'.format(path))
    try:
        tag = read_tag(path)
        if not (tag and tag.artist and tag.title):
            LOG.warn('No ID3 for {0}.'.format(path))
            return
        try:
            artist = session.query(LocalArtist).filter(LocalArtist.name == tag.artist).one()
        except NoResultFound:
            artist = LocalArtist(name=tag.artist)
            session.add(artist)
        track = LocalTrack(url=url, name=tag.title, local_artist=artist)
        session.add(track)
        session.commit()
    except UnicodeEncodeError:
        LOG.warn('Cannot encode ID3 for {0}.'.format(path))
        session.rollback()
    except NoTagError:
        LOG.warn('Cannot read ID3 for {0}.'.format(path))


if __name__ == '__main__':
    basicConfig(level=INFO)
    scan_config()

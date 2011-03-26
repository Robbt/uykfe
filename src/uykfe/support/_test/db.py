
from logging import basicConfig, DEBUG
from unittest import TestCase

from uykfe.support.db import open_db, delete_db, LocalArtist
from uykfe._test import TEST_DIR


class TestDb(TestCase):
    
    def test_open(self):
        basicConfig(level=DEBUG)
        assert open_db(dir=TEST_DIR)()
    
    def test_create_local_artist(self):
        delete_db(dir=TEST_DIR)
        session_factory = open_db(dir=TEST_DIR)
        session = session_factory()
        artist = LocalArtist('test artist')
        session.add(artist)
        assert not artist.id
        session.commit()
        assert artist.id
        session.close()
        session = session_factory()
        assert session.query(LocalArtist).count()
        artists = session.query(LocalArtist).all()
        assert len(artists) == 1, artists
        assert artists[0].name == 'test artist', artists[0]

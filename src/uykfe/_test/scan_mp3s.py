
from logging import basicConfig, DEBUG
from unittest import TestCase

from uykfe.scan_mp3s import scan_dirs
from uykfe.support.db import delete_db, open_db, LocalArtist, LocalTrack
from uykfe._test import TEST_DIR


class ScanMp3sTest(TestCase):
    
    def test_scan_mp3s(self):
        basicConfig(level=DEBUG)
        delete_db(dir=TEST_DIR)
        session = open_db(dir=TEST_DIR)()
        artist = LocalArtist(name='test artist')
        session.add(artist)
        track = LocalTrack(name='test track', url='test url', local_artist=artist.id)
        session.add(track)
        session.flush()
        assert session.query(LocalTrack).filter(LocalTrack.url == track.url).count() == 1
        scan_dirs(session, ['/home/andrew/projects/personal/uykfe/data'])
        assert session.query(LocalTrack).filter(LocalTrack.url == track.url).count() == 0
        


from logging import basicConfig, DEBUG
from unittest import TestCase

from uykfe.scan_mp3s import scan_dirs
from uykfe.support.db import delete_db, open_db
from uykfe._test import TEST_DIR
from uykfe.identify_artists import identify_artists


class IdentifyArtistsTest(TestCase):
    
    def test_identify_artists(self):
        basicConfig(level=DEBUG)
        delete_db(dir=TEST_DIR)
        session = open_db(dir=TEST_DIR)()
        scan_dirs(session, ['/home/andrew/projects/personal/uykfe/data'])
        session.commit()
        identify_artists(dir=TEST_DIR)

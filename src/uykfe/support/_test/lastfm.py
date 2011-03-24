
from logging import basicConfig, DEBUG
from pprint import pprint
from unittest import TestCase

from uykfe.support.lastfm import LastFm
from uykfe._test import TEST_DIR


class LastFmTest(TestCase):
    
    def test_track_search(self):
        basicConfig(level=DEBUG)
        lastfm = LastFm(dir=TEST_DIR)
        pprint(lastfm.track_search('all i need is a miracle'), indent=2)
        print(list(lastfm.artists_for_track('once more in the')))

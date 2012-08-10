
from logging import basicConfig, DEBUG
from unittest import TestCase

from uykfe.support.squeeze import SqueezeServer


class SqueezeTest(TestCase):
    
    def test_name(self):
        basicConfig(level=DEBUG)
        squeeze = SqueezeServer(address='block', port=9090, player='HiFi')
        # only when cleared
        #assert squeeze.playlist_remaining == 0, squeeze.playlist_remaining
        assert isinstance(squeeze.playlist_remaining, int)

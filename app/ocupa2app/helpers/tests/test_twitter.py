import unittest
import unittest.mock
from twitter import Twitter

class TwitterTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'pablo@docecosas.com'
        self.token = '8i4tBARfJmGrZnfdBt3I'
        self.tw = Twitter(self.user_id, token=self.token)
        pass

    def test_get_token(self):
        t = Twitter(self.user_id)
        token = t.get_token()

    def test_token(self):
        i = Twitter(self.user_id, token=self.token)
        # TODO: There's no ping :-(

    def test_get_posts_by_hashtag(self):
        posts = self.tw.get_posts_by_hashtag('pizza')
        assert posts is not None

import unittest
import unittest.mock
from instagram import Instagram

class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'pablo@docecosas.com'
        self.token = '8i4tBARfJmGrZnfdBt3I'
        self.ig = Instagram(self.user_id, token=self.token)
        pass

    def test_get_token(self):
        i = Instagram(self.user_id)
        token = i.get_token()

    def test_token(self):
        i = Instagram(self.user_id, token=self.token)
        # TODO: There's no ping :-(

    def test_get_hashtag(self):
        hashtag_id = self.ig.get_hashtag('porsche')
        self.assertEqual(hashtag_id, 288)

    def test_get_hashtag_non_existant(self):
        hashtag_id = self.ig.get_hashtag('Kwyjibo')
        assert hashtag_id is None

    def test_get_recent_posts(self):
        posts = self.ig.get_recent_posts(21)
        assert posts is not None

    def test_get_top_posts(self):
        posts = self.ig.get_top_posts(21)
        assert posts is not None

    def test_get_media(self):
        media = self.ig.get_media(10372)
        assert media is not None

    def test_get_user(self):
        user = self.ig.get_user(74)
        assert user is not None

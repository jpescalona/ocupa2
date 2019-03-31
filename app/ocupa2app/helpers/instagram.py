from ocupa2app.models import *
import logging
from constance import config
from ocupa2app.helpers import APIBase


class Instagram(APIBase):

    BASE_URL = 'http://hackathon.ocupa2.com/instagram/'

    def __init__(self, user_id, token=None):
        self.token = token
        self.user_id = user_id
        self.hashtag_cache = dict()
        self.user_cache = dict()
        self.media_cache = dict()
        super().__init__()

    def get_token(self):
        if not self.user_id:
            raise KeyError("You must specify the user_id")
        url = Instagram.BASE_URL + 'get/key'
        d = self.get(url, {'email': self.user_id}, skip_operation=True)
        self.token = d.json()['key']
        return self.token

    def get_hashtag(self, hashtag):
        """ Returns the ID of a hashtag """
        if hashtag not in self.hashtag_cache:
            url = Instagram.BASE_URL + 'ig_hashtag_search'
            params = {'q': hashtag, 'user_id': self.user_id }
            d = self.get(url, params)
            j = d.json()
            if 'id' not in j:
                return None
            self.hashtag_cache[hashtag] = j['id']
        return self.hashtag_cache[hashtag]

    def get_recent_posts(self, hashtag_id):
        url = Instagram.BASE_URL + '{id}/recent_media'.format(id=hashtag_id)
        params = {'user_id': self.user_id}
        d = self.get(url, params)
        try:
            return d.json()['data']
        except:
            return []
    
    def get_top_posts(self, hashtag_id):
        url = Instagram.BASE_URL + '{id}/top_media'.format(id=hashtag_id)
        params = {'user_id': self.user_id}
        d = self.get(url, params)
        try:
            return d.json()['data']
        except:
            return []

    def get_media(self, media_id):
        if media_id not in self.media_cache:
            url = Instagram.BASE_URL + 'media/{id}'.format(id=media_id)
            params = {'fields': 'id,comments_count,like_count,media_type,username'}
            d = self.get(url, params)
            self.media_cache[media_id] = d.json()[0]
        return self.media_cache[media_id]

    def get_user(self, user_id):
        if user_id not in self.user_cache:     
            url = Instagram.BASE_URL + '{id}'.format(id=user_id)
            params = {'fields': 'id,username,media_count,follower_count'}
            d = self.get(url, params)
            self.user_cache[user_id] = d.json()[0]
        return self.user_cache[user_id]

    def extend_posts(self, posts):
        """ Adds to each post the username field added to the posts. """
        for post in posts:
            media = self.get_media(post['id'])
            post['username'] = media[0]['userId']

    def follow(self, user_id):
        url = Instagram.BASE_URL + '{id}/follow'.format(id=user_id)
        params = {'action': 'follow'}
        d = self.get(url, params)
        return d

    def unfollow(self, user_id):
        url = Instagram.BASE_URL + '{id}/follow'.format(id=user_id)
        params = {'action': 'unfollow'}
        d = self.get(url, params)
        return d

    def like(self, post_id):
        url = Instagram.BASE_URL + '{id}/like'.format(id=post_id)
        params = {'action': 'like'}
        d = self.get(url, params)
        return d

    def unlike(self, post_id):
        url = Instagram.BASE_URL + '{id}/like'.format(id=post_id)
        params = {'action': 'unlike'}
        d = self.get(url, params)
        return d


def fetch_posts_and_users_for_tag(tag, logger=None, max_operations=None):
    """ It will download and store every item in the model """
    if not logger:
        logger = logging.getLogger(__name__)
    if max_operations and max_operations < 4:
        logger.warning('We cannot fetch data for %s as the maximum operations %s would not allow', tag, max_operations)
        return
    ig = Instagram(config.INSTAGRAM_ACCOUNT)
    logger.info('Getting social_network')
    social_network = SocialNetwork.nodes.get_or_none(name='instagram')
    if social_network is None:
        social_network = SocialNetwork.create({'name': 'instagram'})[0]
    logger.info('Found %s', social_network)
    logger.info('Fetching posts for tag %s', tag)
    hashtag_id = ig.get_hashtag(tag)
    recent_posts = ig.get_recent_posts(hashtag_id)
    logger.info('Fetched %d recent posts', len(recent_posts))
    top_posts = ig.get_top_posts(hashtag_id)
    logger.info('Fetched %d top posts', len(top_posts))
    posts = recent_posts + top_posts
    for post in posts:
        IP = InstagramPost.nodes.get_or_none(uid=post['id'])
        if IP is None:
            logger.info('Creating post %s', post['id'])
            IP = InstagramPost.create({'uid': post['id'],'like_count': post['likeCount'],'comment_count': post['commentsCount'],'media_type': post['mediaType']})[0]
            logger.info('Fetching for media %s', post['id'])
            media = ig.get_media(post['id'])
            logger.info('Fetched %s', post['id'])
            user_id = media['userId']
            user = social_network.user.get_or_none(uid=user_id)
            logger.info('Found user %s', user) 
            if not user:
                user_data = ig.get_user(user_id)
                logger.info('Fetched user %s', user_data)
                user = User.create({'uid': user_id, 'name': user_data['username'], 'media_count': user_data['mediaCount'], 'follower_count': user_data['followerCount']})[0]
                logger.info('Created user %s', user)
                user.social_network.connect(social_network)
                logger.info('Created user %s', user)
            user.post.connect(IP)
            IP.user.connect(user)
            logger.info('Created %s', IP)
        logger.info('Connecting post %s to %s', post['id'], tag)
        hashtag = HashTag.nodes.get(name=tag)
        IP.hashtags.connect(hashtag)
        hashtag.posts.connect(IP)

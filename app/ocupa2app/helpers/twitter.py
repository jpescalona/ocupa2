from ocupa2app.helpers import APIBase
import logging
from ocupa2app.models import TwitterPost, SocialNetwork, HashTag, User
from constance import config


class Twitter(APIBase):

    BASE_URL = 'http://hackathon.ocupa2.com/twitter/1.1/'

    def __init__(self, user_id, token=None):
        self.token = token
        self.user_id = user_id
        self.cache = dict()
        super().__init__()

    def get_token(self):
        if not self.user_id:
            raise KeyError("You must specify the user_id")
        url = Twitter.BASE_URL + 'get/key'
        d = self.get(url, {'email': self.user_id}, skip_operation=True)
        self.token = d.json()['key']
        return self.token

    def get_posts_by_hashtag(self, hashtag):
        """ Returns a list of tweets """
        url = Twitter.BASE_URL + 'search/tweets.json'
        params = {'q': hashtag}
        d = self.get(url, params)
        return d.json()

    def get_post(self, tweet_id):
        """ Returns a single post """
        url = Twitter.BASE_URL + 'statuses/retweets/{id}.json'.format(id=tweet_id)
        d = self.get(url)
        return d.json()[0]

    def follow(self, user_id):
        url = Twitter.BASE_URL + 'friendships/create.json?user_id={id}'.format(id=user_id)
        d = self.get(url)
        return d

    def unfollow(self, user_id):
        url = Twitter.BASE_URL + 'friendships/destroy.json?user_id={id}'.format(id=user_id)
        d = wself.get(url)
        return d

def fetch_posts_and_users_for_tag(tag, logger=None, max_operations=None):
    if not logger:
        logger = logging.getLogger(__name__)
    if max_operations and max_operations < 4:
        logger.warning('We cannot fetch data for %s as the maximum operations %s would not allow', tag, max_operations)
        return
    tw = Twitter(config.TWITTER_ACCOUNT)
    logger.info('Getting social_network')
    social_network = SocialNetwork.nodes.get_or_none(name='twitter')
    if social_network is None:
        social_network = SocialNetwork.create({'name': 'twitter'})[0]
    """ It will download and store every item in the model """
    logger.info('Fetching tweets for tag %s', tag)
    posts = tw.get_posts_by_hashtag(tag)
    logger.info('Fetched %d tweets', len(posts))
    for post in posts:
        TP = TwitterPost.nodes.get_or_none(uid=post['tweetId'])
        if TP is None:
            media = tw.get_post(post['tweetId'])
            logger.info('Creating post %s', post['tweetId'])
            TP = TwitterPost.create({'uid': post['tweetId'],'like_count': media['likeCount'],'reply_count': media['replyCount'],'retweeted_count': media['retweetCount']})[0]
            logger.info('Created %s from %s', TP, post)
            user_id = post['userid']
            user = social_network.user.get_or_none(uid=user_id)
            logger.info('Found user %s', user)
            if not user:
                user = User.create({'uid': user_id, 'name': post['name']})[0]
                logger.info('Created user %s', user)
                user.social_network.connect(social_network)
                logger.info('Created user %s', user)
            user.post.connect(TP)
        logger.info('Connecting post %s to %s', post['tweetId'], tag)
        TP.hashtags.connect(HashTag.nodes.get(name=tag))

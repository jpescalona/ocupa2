from celery.task import task
from celery.utils.log import get_task_logger
from .models import SocialNetwork, Category, InstagramKarma, TwitterKarma
from .helpers.instagram import Instagram
from .helpers.twitter import Twitter
from constance import config
from pinax.eventlog.models import log
import neomodel
import statistics 


logger = get_task_logger(__name__)


@task(bind=True)
def refresh_social_network(self, social_network_name, categories=[], max_operations=None):
    print(logger)
    try:
        helper_module_name = '{}.helpers.{}'.format(
            SocialNetwork.__module__.split('.')[0],
            social_network_name.lower())
        helper_module = __import__(helper_module_name, fromlist=[None])
    except neomodel.core.DoesNotExist:
        logger.error("REFRESHING social network {} does not exist. QUITTING!".format(social_network_name))
    except ImportError:
        logger.error("REFRESHING social network {} is not supported. QUITTING!".format(social_network_name))
    logger.info('Fetching categories %s', categories)
    for c in categories:
        logger.info('Fetching tags for category %s', c)
        category = Category.nodes.get(name=c)
        tags = [t.name for t in category.hashtags.all()]
        for tag in tags:
            logger.info('Fetching posts for tag %s', tag)
            helper_module.fetch_posts_and_users_for_tag(tag, logger=logger, max_operations=max_operations)

def get_karma_for(user, attribute):
    """ Returns karma calculated for the Posts of an user using
    the attribute parameter as the property to evaluate """
    counts = [getattr(p, attribute) for p in user.post.all()]
    stdev = statistics.stdev(counts)
    if stdev == 0:
        stdev = 0.1
    median = statistics.median(counts)
    karma = round(100*median/stdev)
    return karma

def get_likes_karma(user):
    return get_karma_for(user, 'like_count')

def get_replies_karma(user):
    return get_karma_for(user, 'reply_count')

def get_retweets_karma(user):
    return get_karma_for(user, 'retweeted_count')

def get_comments_karma(user):
    return get_karma_for(user, 'comment_count')

def get_karma(user):
    karma = {'likes': get_likes_karma(user)}
    if user.social_network.single().name.lower() == 'instagram':
        karma.update({
            'comments': get_comments_karma(user),
        })
    elif user.social_network.single().name.lower() == 'twitter':
        karma.update({
            'replies': get_replies_karma(user),
            'retweets': get_retweets_karma(user),
        })
    else:
        karma = {}
    return karma


def follow_the_user(user):
    if user.social_network.single().name.lower() == 'instagram':
        iq = Instagram(config.INSTAGRAM_ACCOUNT)
        iq.follow(user.uid)
    elif user.social_network.single().name.lower() == 'twitter':
        tq = Twitter(config.TWITTER_ACCOUNT)
        tq.follow(user.uid)

def unfollow_the_user(user):
    if user.social_network.single().name.lower() == 'instagram':
        iq = Instagram(config.INSTAGRAM_ACCOUNT)
        iq.unfollow(user.uid)
    elif user.social_network.single().name.lower() == 'twitter':
        tq = Twitter(config.TWITTER_ACCOUNT)
        tq.unfollow(user.uid)

def shall_we_follow_the_user(karma):
    if karma.user.single().social_network.single().name.lower() == 'instagram':
        return karma.likes > config.KARMA_MINIMUM_LIKES and karma.comments > config.KARMA_MINIMUM_INSTAGRAM_COMMENTS
    elif karma.user.single().social_network.single().name.lower() == 'twitter':
        return karma.likes > config.KARMA_MINIMUM_LIKES and karma.replies > config.KARMA_MINIMUM_TWITTER_REPLIES \
               and karma.retweets > config.KARMA_MINIMUM_TWITTER_RETWEETS
    else:
        return False

@task(bind=True)
def calculate_karma(self, social_network_name, categories=[]):
    for category in categories:
        category = Category.nodes.get(name=category)
        social_network = SocialNetwork.nodes.get(name=social_network_name)

        for user in social_network.user.all():
            # Calculate the karma for this social network
            new_karma = get_karma(user)
            current_karma = user.karma.get_or_none()
            if current_karma is None:
                # Create Karma for this social network
                if social_network_name.lower() == 'instagram':
                    current_karma = InstagramKarma.create(new_karma)[0]
                elif social_network_name.lower() == 'twitter':
                    current_karma = TwitterKarma.create(new_karma)[0]

                current_karma.user.connect(user)
                current_karma.category.connect(category)
            else:
                current_karma.__dict__.update(new_karma)
                current_karma.save()

            logger.info('Evaluating karma for %s (%s)', user, current_karma)
            if shall_we_follow_the_user(current_karma):
                logger.info('We must follow the user')
                if not user.is_followed:
                    follow_the_user(user)
                    user.is_followed = True
                    user.save()
                    log(
                        user=None,
                        action="FOLLOW_USER",
                        extra={
                            "title": "Automatically followed user {} on {}".format(user.name, social_network.name),
                            "user": user.name,
                            "social_network": social_network.name
                        }
                    )
            else:
                if user.is_followed:
                    unfollow_the_user(user)
                    user.is_followed = False
                    user.save()
                    log(
                        user=None,
                        action="UNFOLLOW_USER",
                        extra={
                            "title": "Automatically unfollowed user {} on {}".format(user.name, social_network.name),
                            "user": user.name,
                            "social_network": social_network.name
                        }
                    )


def shall_we_like_the_post(post):
    return post.user.follower_count > config.FOLLOWERS_MINIMUM_COUNT and \
           post.user.media_count > config.POSTED_POSTS_MINIMUM_COUNT and \
           post.like_count > config.LIKES_MINIUM_COUNT


def like_the_post(post, social_network):
    if social_network.name.lower() == 'instagram':
        iq = Instagram(config.INSTAGRAM_ACCOUNT)
        iq.like(post.uid)
    elif social_network.name.lower() == 'twitter':
        it = Twitter(config.TWITTER_ACCOUNT)
        it.like(post.uid)


def unlike_the_post(post, social_network):
    if social_network.name.lower() == 'instagram':
        iq = Instagram(config.INSTAGRAM_ACCOUNT)
        iq.like(post.uid)
    elif social_network.name.lower() == 'twitter':
        it = Twitter(config.TWITTER_ACCOUNT)
        it.like(post.uid)

@task(bind=True)
def like_posts(self, social_network_name):
    social_network = SocialNetwork.nodes.get(name=social_network_name)

    # We will gather the users ordered by not followed and their follower count
    for user in social_network.user.order_by('-is_followed', '-follower_count').all():
        for post in user.post.order_by('-is_liked', '-like_count'):
            if shall_we_like_the_post(post):
                if not post.is_liked:
                    like_the_post(post, social_network)
                    post.is_liked = True
                    post.save()
                    log(
                        user=None,
                        action="POST_LIKED",
                        extra={
                            "title": "Automatically liked a post from user {} on {}".format(user.name,
                                                                                              social_network.name),
                            "user": user.name,
                            "social_network": social_network.name
                        }
                    )
            elif shall_we_follow_the_user(post):
                if post.is_liked:
                    unlike_the_post(post, social_network)
                    post.is_liked = False
                    post.save()
                    log(
                        user=None,
                        action="POST_UNLIKED",
                        extra={
                            "title": "Automatically unliked a post from user {} on {}".format(user.name,
                                                                                              social_network.name),
                            "user": user.name,
                            "social_network": social_network.name
                        }
                    )


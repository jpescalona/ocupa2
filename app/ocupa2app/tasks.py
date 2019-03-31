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
def refresh_social_network(self, social_network_name, categories=[]):
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
            helper_module.fetch_posts_and_users_for_tag(tag,logger=logger)

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
    if user.social_network.single().name.lower() == 'Instagram':
        iq = Instagram(config.INSTAGRAM_ACCOUNT)
        iq.follow(user.uid)
    elif user.social_network.single().name.lower() == 'Twitter':
        tq = Twitter(config.TWITTER_ACCOUNT)
        tq.follow(user.uid)

def unfollow_the_user(user):
    if user.social_network.single().name.lower() == 'Instagram':
        iq = Instagram(config.INSTAGRAM_ACCOUNT)
        iq.unfollow(user.uid)
    elif user.social_network.single().name.lower() == 'Twitter':
        tq = Twitter(config.TWITTER_ACCOUNT)
        tq.unfollow(user.uid)

def shall_we_follow_the_user(karma):
    if karma.user.single().social_network.single().name.lower() == 'Instagram':
        return karma.likes > 10 and karma.comments > 3
    elif karma.user.single().social_network.single().name.lower() == 'Tweeter':
        return karma.likes > 10 and karma.replies > 1 and karma.retweets > 10
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


            if shall_we_follow_the_user(current_karma):
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


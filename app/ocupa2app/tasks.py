from celery.task import task
from celery.utils.log import get_task_logger
from .models import SocialNetwork, Category
import neomodel

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
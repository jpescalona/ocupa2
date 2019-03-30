from celery.task import task
from celery.utils.log import get_task_logger
from .models import SocialNetwork
import neomodel

logger = get_task_logger(__name__)


@task(bind=True)
def refresh_social_network(self, social_network_name):
    try:
        helper_module = __import__('{}.helpers.{}'.format(
            SocialNetwork.__module__.split('.')[0],
            social_network_name.lower()))
        social_network = SocialNetwork.nodes.get(name=social_network_name)

        # gather users

        logger.info("REFRESHING social network {}".format(social_network.name))
    except neomodel.core.DoesNotExist:
        logger.error("REFRESHING social network {} does not exist. QUITTING!".format(social_network_name))
    except ImportError:
        logger.error("REFRESHING social network {} is not supported. QUITTING!".format(social_network_name))
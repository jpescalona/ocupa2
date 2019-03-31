from django.core.management.base import BaseCommand, CommandError
from ocupa2app.tasks import refresh_social_network

class Command(BaseCommand):
    help = 'Loads initial data into the social network, specify the categories'

    def add_arguments(self, parser):
        parser.add_argument('social_network', nargs=1, type=str)
        parser.add_argument('categories', nargs='+', type=str)

    def handle(self, *args, **options):
        for social_network in options['social_network']:
            result = refresh_social_network.apply(([social_network]),{'categories': options['categories']})
            print(result)

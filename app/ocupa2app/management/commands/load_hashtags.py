from django.core.management.base import BaseCommand, CommandError
from yaml import load, YAMLError

from ocupa2app.models import Category, HashTag

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Command(BaseCommand):
    help = 'Load list of hashtags per category'

    def add_arguments(self, parser):
        parser.add_argument('data_file', type=str)

    def handle(self, *args, **options):

        try:
            for category_name, hashtags in load(open(options['data_file'], 'r').read(), Loader=Loader).items():
                category = Category.nodes.get_or_none(name=category_name)
                if category is None:
                    category = Category.create({'name': category_name})
                for hashtag_name in hashtags:
                    hashtag = HashTag.nodes.get_or_none(name=hashtag_name)
                    if hashtag is None:
                        hashtag = HashTag.create({'name': hashtag_name})
                    hashtag.category.connect(category)
        except IOError:
            raise CommandError('{} cannot be loaded'.format(options['data_file']))
        except YAMLError:
            raise CommandError('Wrong format of {}'.format(options['data_file']))

        self.stdout.write(self.style.SUCCESS('File {} loaded successfully'.format(options['data_file'])))

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from ocupa2app.models import *

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocupa2.settings')

app = Celery('ocupa2')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

def scheduler_filter(objects):
    """ Esta funcion devolvera una lista de objetos que deben ser cargados
    respecto a la lógica de negocio de cada red social """
    return objects

def scheduler_weight(objects, n=None):
    """ Esta funcion ordena la lista en función a la prioridad. Es posible
    pasarle un argumento n que limitará los elementos """
    return objects


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task(bind=True)
def update_category(self,categories_list=[]):
    """ This will start downloading all the categories """
    if not categories_list:
        categories = Category.nodes.all
    else:
        categories = Category.nodes.filter(name__in=categories_list)
    return categories



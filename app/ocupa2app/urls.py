from django.urls import path
from django.views.generic import TemplateView, ListView
from pinax.eventlog.models import Log

urlpatterns = [
    path(r'', ListView.as_view(model=Log, template_name="home.html"), name="home")
]

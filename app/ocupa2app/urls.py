from django.urls import path
from django.views.generic import TemplateView, ListView
from pinax.eventlog.models import Log
from ocupa2app.views import CategoriesView, EditCategoryView

urlpatterns = [
    path(r'', ListView.as_view(model=Log, template_name="home.html"), name="home"),
    path(r'categories/', CategoriesView.as_view(), name="categories"),
    path(r'categories/edit/<category_id>', EditCategoryView.as_view(), name="edit_category")
]

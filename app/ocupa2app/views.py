from django.views.generic import TemplateView, FormView
from .models import Category, HashTag
from .forms import CategoryForm

class CategoriesView(TemplateView):
    template_name = "categories.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = []
        for category in Category.nodes.all():
            object_list.append({
                'uid': category.uid,
                'name': category.name,
                'hashtags': [hashtag.name for hashtag in category.hashtags.all()],
                'number_of_posts': sum([len(category.posts) for category in category.hashtags.all()]),
            })


        context['object_list'] = object_list
        return context

class EditCategoryView(TemplateView):
    template_name = "edit_category.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = context["form"]
        if form.is_valid():
            try:
                category = Category.nodes.get(uid=self.kwargs.get('category_id'))
                current_hashtags = [hashtag.name for hashtag in category.hashtags.all()]
                modified_hashtags = [modified_hashtag.strip() for modified_hashtag in form.cleaned_data['hashtags'].split(',')]
                for modified_hashtag in modified_hashtags:
                    if modified_hashtag not in current_hashtags:
                        new_hashtag = HashTag.create({'name': modified_hashtag})[0]
                        new_hashtag.category.connect(category)
                        category.hashtags.connect(new_hashtag)

                for current_hashtag in current_hashtags:
                    if current_hashtag not in modified_hashtags:
                        HashTag.nodes.get(name=current_hashtag).delete()
            except Exception as e:
                print(e)

        return super(TemplateView, self).render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.nodes.get(uid=self.kwargs.get('category_id'))
            context['category_name'] = category.name
            if self.request.POST:
                context['form'] = CategoryForm(self.request.POST)
            else:
                context['form'] = CategoryForm(initial={'hashtags': ', '.join(
                    [hashtag.name for hashtag in category.hashtags.all()])})
        except Exception:
            context['form'] = CategoryForm()

        return context
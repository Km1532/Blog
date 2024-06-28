from django.db.models import Count, Q
from .models import Category

def menu(request):
    user_menu = [{'title': "Про сайт", 'url_name': 'about'},
                 {'title': "Додати статтю", 'url_name': 'add_page'},
                 {'title': "Зворотній зв'язок", 'url_name': 'contact'}]

    if request.user.is_authenticated:
        user_menu.insert(1, {'title': "Вийти", 'url_name': 'logout'})
    else:
        user_menu.insert(1, {'title': "Увійти", 'url_name': 'login'})

    return {'menu': user_menu}

class DataMixin:
    paginate_by = 20

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = Category.objects.annotate(num_posts=Count('blog', filter=Q(blog__is_published=True)))

        context['menu'] = menu(self.request)
        context['cats'] = cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0

        return context

from django.urls import path
from django.views.decorators.cache import cache_page
from . import views
from .views import * 

urlpatterns = [
    path('', BlogHome.as_view(), name='home'),
    path('about/', about, name='about'),
    path('addpage/', AddPage.as_view(), name='add_page'),
    path('contact/', contact, name='contact'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', WomenCategory.as_view(), name='category'),
    path('add_comment/<slug:post_slug>/', views.add_comment, name='add_comment'),
    path('add_like/<slug:post_slug>/', views.add_like, name='add_like'),
]

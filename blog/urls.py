from django.urls import path
from django.views.decorators.cache import cache_page
from . import views
from .views import *

urlpatterns = [
    path('', views.BlogHome.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('addpage/', views.AddPage.as_view(), name='add_page'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', views.WomenCategory.as_view(), name='category'),
    path('add_comment/<slug:post_slug>/', views.add_comment, name='add_comment'),
    path('add_like/<slug:post_slug>/', views.add_like, name='add_like'),
    path('post/<slug:post_slug>/like_comment/<int:comment_id>/', views.add_like_comment, name='add_like_comment'),
    path('post/<slug:post_slug>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('post/<slug:post_slug>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('soon/', views.soon_page, name='soon_page'),
    path('profile/', views.profile, name='profile'), 
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.UserProfile.as_view(), name='user_profile'),
]

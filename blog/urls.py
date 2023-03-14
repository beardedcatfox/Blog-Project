from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('login/', LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('create_post', views.create_post, name="create_post"),
    path('post_detail/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/update/', views.update_post, name='update_post'),
    path('post_list', views.PostListView.as_view(), name='post_list'),
    path('user/<str:username>/', views.UserPostListView.as_view(), name='user_posts'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('contact_us/', views.contact, name='contact_us'),
    path('unpublished_posts/', views.unpublished_posts, name='unpublished_posts'),
    path('password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('logout/', views.logout_view, name='logout'),
]

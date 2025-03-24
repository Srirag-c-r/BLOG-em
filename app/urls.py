from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('blog/list/', views.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('blog/create/', views.post_create, name='post_create'),
    path('blog/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('blog/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('blog/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('blog/<int:post_id>/like/', views.like_post, name='like_post'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('bloggers/', views.blogger_list, name='blogger_list'),
    path('blogger/<int:author_id>/', views.blogger_detail, name='blogger_detail'),
    path('search/', views.search, name='search'),
    path('clear-welcome-toast/', views.clear_welcome_toast, name='clear_welcome_toast'),
    path('blog/<int:post_id>/save/', views.save_post, name='save_post'),
    path('saved-posts/', views.saved_posts, name='saved_posts'),
] 
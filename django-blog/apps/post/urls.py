from django.urls import path
from .views import post_list, post_detail, post_create, post_edit, post_delete

urlpatterns = [
    path('', post_list, name='post_list'),
    path('post/create/', post_create, name='post_create'),
    path('post/<slug:slug>/', post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', post_delete, name='post_delete'),
]


from django.conf.urls import url, include
from django.contrib import admin
from myblog import views

urlpatterns = [
    url(r'^(?P<home_page_id>\d+)/', views.index),
    url(r'((?P<user_site>\w+)/article/(?P<article_id>\d+))', views.article_detail),
    url(r'poll/$', views.poll),
    url(r'(?P<user_site>\w+)/article/(?P<condition>category|tags|date)/(?P<para>\w+)', views.home_site),
    url(r'comment/$', views.comment),
    url(r'comment1/$', views.comment1),
    url(r'(?P<user_site>\w+)', views.home_site)

]

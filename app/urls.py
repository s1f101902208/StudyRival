from django.conf.urls import include, url
import django.contrib.auth.views
from . import views

urlpatterns = [
    url(r'^ranking/$', views.ranking, name='ranking'),
    url(r'^mypage/$', views.mypage, name='mypage'),
    url(r'^timer/$', views.timer, name='timer'),
    url(r'^tweet/$', views.tweet, name='tweet'),
    url(r'', include('social_django.urls', namespace = 'social')),
    url(r'', include('easy_regist.urls', namespace='easy_regist')),
    ]

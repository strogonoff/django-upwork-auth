# coding: utf-8

from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^authenticate/', views.oauth_login,
        name='upwork_oauth_login'),
    url(r'^callback/', views.OAuthLoginCallback.as_view(),
        name='upwork_oauth_login_callback'),
)

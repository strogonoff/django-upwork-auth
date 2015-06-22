# coding: utf-8

from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout

from django.contrib import admin
admin.autodiscover()

from . import views

urlpatterns = patterns(
    '',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^auth/', include('django_upwork_auth.urls')),
    url(r'^$', views.GuestView.as_view(), name='guest_page'),
    url(r'^member/$', views.MemberView.as_view(), name='member_page'),
)

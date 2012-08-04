from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from paste.views import *

urlpatterns = patterns('',
    url('^changelog/$', TemplateView.as_view(template_name='changelog.html'),
        name='changelog'),
    url('^logout/$', logout_view, name='logout'),
    url('^paste/$', AddSnippetView.as_view()),
    url('^syntax/$', SyntaxView.as_view()),
    url('^(?P<slug>[\w\d]+)/delete/$', DeleteSnippetView.as_view()),
    url('^(?P<a>[\w\d]+)\.\.\.(?P<b>[\w\d]+)$', DiffView.as_view()),
    url('^$', IndexView.as_view()),
    url('^u/(?P<slug>[\w\d]+)/$', UserView.as_view()),
    url(r'^browserid/', include('django_browserid.urls')),
    # Examples:
    # url(r'^$', 'pasteapp.views.home', name='home'),
    # url(r'^pasteapp/', include('pasteapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url('^(?P<slug>[\w\d]+)/?$', SnippetView.as_view()),
)


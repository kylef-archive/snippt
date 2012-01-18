from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from paste.views import IndexView, PasteView, DiffView

urlpatterns = patterns('',
    url('^(?P<slug>[\w\d]+)$', PasteView.as_view()),
    url('^(?P<a>[\w\d]+)...(?P<b>[\w\d]+)$', DiffView.as_view()),
    url('^$', IndexView.as_view()),
    # Examples:
    # url(r'^$', 'pasteapp.views.home', name='home'),
    # url(r'^pasteapp/', include('pasteapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls))
)


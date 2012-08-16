from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cv.views',
    url(r'^$', 'cvlist'),
	url(r'^cv/$', 'cvlist'),
	url(r'^test/$', 'index'),
	url(r'^media/photos/(?P<file_name>[A-Za-z0-9_\-]+).jpg/$', 'getjpg'),
	url(r'^cv/odt/$', 'odtlist'),
	url(r'^cv/odt/(?P<person_id>\d+)/$', 'odt'),
	url(r'^cv/(?P<cv_id>\d+)/$', 'detail'),
	url(r'^cv/\d+/odt/$', 'odtjson'),
	url(r'^cv/(?P<cv_id>\d+)/(?P<lang>eng)/$', 'detail'),
	url(r'^cv/(?P<cv_id>\d+)/(?P<arg1>eng|doc)/(?P<arg2>eng|doc)/$', 'detail'),
    # Examples:
    # url(r'^$', 'cvapp.views.home', name='home'),
    # url(r'^cvapp/', include('cvapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

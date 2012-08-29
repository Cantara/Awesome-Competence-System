from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cv.views',
    url(r'^$', 'cvlist'),
	url(r'^cv/$', 'cvlist'),
	url(r'^cv/(?P<cv_id>\d+)/$', 'detail'),
	url(r'^cv/\d+/download/$', 'download'),
	url(r'^cv/\d+/download/(?P<format>pdf|doc|odt)/$', 'download'),
	url(r'^cv/(?P<cv_id>\d+)/(?P<lang>eng)/$', 'detail'),
	url(r'^login/$', 'mylogin'),
	url(r'^logout/$', 'mylogout'),
    # Examples:
    # url(r'^$', 'cvapp.views.home', name='home'),
    # url(r'^cvapp/', include('cvapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cv.views',

    url(r'^$', 'cvlist'),
	url(r'^cv/$', 'cvlisted'),
	url(r'^cv/(?P<cv_id>\d+)/$', 'detail'),
	url(r'^cv/(?P<cv_id>\d+)/(?P<lang>eng)/$', 'detail'),
	url(r'^cv/\d+/download/$', 'download'),
	url(r'^cv/\d+/download/(?P<format>pdf|doc|odt)/$', 'download'),

	url(r'^login/$', 'mylogin'),
	url(r'^logout/$', 'mylogout'),

    url(r'^matrix/$', 'matrices'),
    url(r'^matrix/edit/$', 'editmatrix'),
    url(r'^matrix/edit/(?P<m_id>\d+)/$', 'editmatrix'),
    url(r'^matrix/save/$', 'savematrix'),
    url(r'^matrix/addcompetence/$', 'addcompetence'),
    url(r'^matrix/addgroup/$', 'addgroup'),

    url(r'^matrix/(?P<m_id>\d+)/$', 'matrixentry'),
    url(r'^matrix/addentry/$', 'addentry'),
    url(r'^matrix/loadentry/$', 'loadentry'),

    # Examples:
    # url(r'^$', 'cvapp.views.home', name='home'),
    # url(r'^cvapp/', include('cvapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cv.views',

    url(r'^$', 'cv_list'),
    url(r'^cv/$', 'cv_list', name='cv_list'),
    url(r'^cv/multi/$', 'multicv', name='cv_multi'),
    url(r'^cv/(?P<cv_id>\d+)/$', 'detail', name='cv_detail'),
    url(r'^cv/(?P<cv_id>\d+)/(?P<lang>en)/$', 'detail', name='cv_detail_en'),

    url(r'^cv/addcvforperson/(?P<pid>\w+)/$', 'add_cv_for_person', name='cv_add_cv_for_person'),
    
    url(r'^cv/download/$', 'download', name='cv_download'),
    url(r'^cv/download/(?P<format>pdf|doc|odt)/$', 'download', name='cv_download_format'),

    url(r'^cv/expautocomplete/$', 'expautocomplete', name='cv_expautocomplete'),

    url(r'^cv/nagmail/$', 'nagmail', name='cv_nagmail'),
    url(r'^cv/multinagmail/$', 'multinagmail', name='cv_multinagmail'),

    url(r'^changelog/$', 'changelog', name='changelog'),
    url(r'^multisearch/$', 'multisearch', name='multisearch'),

    url(r'^login/$', 'myRemoteLogin'),
    url(r'^logout/$', 'myRemoteLogout'),

    url(r'^matrix/$', 'matrix_list'),
    url(r'^matrix/edit/$', 'matrix_edit'),
    url(r'^matrix/edit/(?P<m_id>\d+)/$', 'matrix_load'),
    url(r'^matrix/edit_bb/(?P<m_id>\d+)/$', 'matrix_load_bb', name='loadmatrix_bb'),
    url(r'^matrix/save/$', 'matrix_save'),

    url(r'^matrix/addcompetence/$', 'addcompetence'),
    url(r'^matrix/addgroup/$', 'addgroup'),
    url(r'^matrix/addexppicker/$', 'addexppicker'),

    url(r'^matrix/ajax/competence/$', 'ajaxcompetencelist'),

    url(r'^matrix/(?P<m_id>\d+)/$', 'matrix_entry_get'),
    url(r'^matrix/(?P<m_id>\d+)/all/$', 'matrix_entry_get_all'),
    url(r'^matrix/saveentry/$', 'matrix_entry_save'),
    url(r'^matrix/loadentry/$', 'matrix_entry_load'),

    # Examples:
    # url(r'^$', 'cvapp.views.home', name='home'),
    # url(r'^cvapp/', include('cvapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^search/', include('haystack.urls')),

)

from django.conf import settings

if settings.DEBUG or True:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/www/media'}),
    )
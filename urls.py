from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Haystack
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView
from haystack.views import SearchView, search_view_factory

sqs = SearchQuerySet().facet('name').facet('location').facet('department')

urlpatterns = patterns('cv.views',

    url(r'^$', 'cv_list'),
    url(r'^cv/$', 'cv_list', name='cv_list'),
    url(r'^cv/multi/$', 'multicv', name='cv_multi'),
    url(r'^cv/(?P<cv_id>\d+)/$', 'detail', name='cv_detail'),
    url(r'^cv/(?P<cv_id>\d+)/(?P<lang>eng)/$', 'detail', name='cv_detail_en'),
    url(r'^cv/download/$', 'download', name='cv_download'),
    url(r'^cv/download/(?P<format>pdf|doc|odt)/$', 'download', name='cv_download_format'),
    url(r'^cv/nagmail/$', 'nagmail', name='cv_nagmail'),
    url(r'^cv/multinagmail/$', 'multinagmail', name='cv_multinagmail'),

    url(r'^changelog/$', 'changelog', name='changelog'),
    url(r'^multisearch/$', 'multisearch', name='multisearch'),

    url(r'^login/$', 'myRemoteLogin'),

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
    url(r'^fsearch/', FacetedSearchView(form_class=FacetedSearchForm, searchqueryset=sqs), name='haystack_search'),
    url(r'^ajaxsearch/', search_view_factory(view_class=SearchView, template='search/ajaxsearch.html', searchqueryset=sqs, load_all=False), name='ajax_search'),

)
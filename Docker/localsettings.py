ADMINS = (
    ('acs-admin', 'acs@cantara.no'),
)

ALLOWED_HOSTS = ['localhost']

MANAGERS = ADMINS

DEBUG = True
TEMPLATE_DEBUG = DEBUG

HTTP_AUTH = ''
APP_URL = 'https://localhost'

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME': 'acs',
        'USER': 'acsuser',
        'PASSWORD': 'acspw',
        'HOST': 'localhost',
        'PORT': '5432',
        },
    }

# Whydah App Auth
APP_NAME = 'ACS'
APP_SECRET = 'ACS_WHYDAH_SECRET'

SSO_URL = '{{sso_url}}'

TESTTOKEN = ''

TESTTOKEN2 = ''

# SOLR
SOLRURL = 'https://{{solr_username}}:{{solr_password}}@'+ALLOWED_HOSTS[0]+'/solr/acs/select'

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
        'ENGINE':'django.db.backends.postgresql',
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

SSO_URL = 'https://sso.cantara.no/sso'

TESTTOKEN = ''

TESTTOKEN2 = ''

# SOLR
SOLRURL = 'http://localhost:8983/solr/select'

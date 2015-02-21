ADMINS = (
    ('{{django_admin_user}}', '{{django_admin_email}}'),
)

ALLOWED_HOSTS = ['{{frontend_server_name}}']

MANAGERS = ADMINS

DEBUG = True
TEMPLATE_DEBUG = DEBUG

HTTP_AUTH = ''
APP_URL = 'https://'+ALLOWED_HOSTS[0]

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME': '{{db_ident}}',
        'USER': '{{db_user}}',
        'PASSWORD': '{{db_password}}',
        'HOST': '{{db_host}}',
        'PORT': '{{db_port}}',
        },
    }

# Whydah App Auth
APP_NAME = '{{acs_app_name}}'
APP_SECRET = '{{acs_secret}}'

SSO_URL = '{{sso_url}}'

TESTTOKEN = ''

TESTTOKEN2 = ''

# SOLR
SOLRURL = 'https://{{solr_username}}:{{solr_password}}@'+ALLOWED_HOSTS[0]+'/solr/acs/select'

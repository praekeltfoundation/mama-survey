DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'survey_test.sqlite',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.comments',

    'jmbo',
    'category',
    'photologue',
    'publisher',
    'secretballot',
    'post',
    'survey',
    'south'
)

STATIC_URL = ''
SITE_ID = 1

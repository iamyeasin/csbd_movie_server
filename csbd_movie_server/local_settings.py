
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '084*v1ufo2d2qiv-u=fj=$jlsjg!xq+#((5zm=pe_)w(3q=6n#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['103.83.15.87']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'csbd_movie_server',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}



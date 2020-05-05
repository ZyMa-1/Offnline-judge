import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SECRET_KEY = "Offnline judge"
CACHE_TYPE = "null"

import os

SQLALCHEMY_DATABASE_URI = os.environ.get('sqlite:///db.sqlite3')
SECRET_KEY = "Offnline judge"
CACHE_TYPE = "null"

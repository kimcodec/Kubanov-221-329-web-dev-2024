import os

import os

SECRET_KEY = b'afd41e94b269e053cc3f6d065a717cffde51ee5208928463ce897faed531006b'

DB_USER = os.environ.get('DB_USER')
if DB_USER is None:
    DB_USER = 'postgres'

DB_PASSWORD = os.environ.get('DB_PASSWORD')
if DB_PASSWORD is None:
    DB_PASSWORD = 'postgres'

DB_HOST = os.environ.get('DB_HOST')
if DB_HOST is None:
    DB_HOST = 'localhost'

DB_NAME = os.environ.get('DB_NAME')
if DB_NAME is None:
    DB_NAME = 'postgres'

DB_PORT = os.environ.get('DB_PORT')
if DB_PORT is None:
    DB_PORT = 5432

ADMIN_ROLE_ID = 1

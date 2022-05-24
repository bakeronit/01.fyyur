from settings import DB_NAME, DB_USER, DB_PASSWD, SEC_KEY
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
class DatebaseURI:
    DATABASE_NAME = DB_NAME
    username = DB_USER
    password = DB_PASSWD
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = f"postgres://{username}:{password}@{url}/{DATABASE_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = SEC_KEY
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
class DatebaseURI:
    DATABASE_NAME = "fyyur"
    username = 'postgres'
    password = 'postgres'
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = f"postgres://{username}:{password}@{url}/{DATABASE_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '44e74c7371064a7283523091d1c70f7f'
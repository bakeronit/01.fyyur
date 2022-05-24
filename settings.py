from dotenv import load_dotenv
import os
load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWD = os.environ.get("DB_PASSWD")
SEC_KEY = os.environ.get("SEC_KEY")

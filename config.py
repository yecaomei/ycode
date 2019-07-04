import os
from datetime import timedelta

DEBUG = True
SECRET_KEY = os.urandom(24)

DIALECT = 'mysql'
DRIVER ='pymysql'
USERNAME = 'root'
PASSWORD = 'a1111111'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'yll'

SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8".format(DIALECT,DRIVER,USERNAME,PASSWORD,HOST,PORT,DATABASE)

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)
WTF_CSRF_ENABLED = False
from flask import Flask
from datetime import timedelta
from flask_pymongo import PyMongo
from config import config
from controller.database import ManagerDBMongo

from flask_wtf.csrf import CsrfProtect
# from flask_cache import Cache

csrf = CsrfProtect()

def create_app(config_name):

    # 初始化app
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化csrf
    csrf.init_app(app)

    # 设置缓存时间为1s
    #app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
    return app



ManagerDBMongo.init_db(db='mydatabase_test', col='users2')
col_users = ManagerDBMongo.get_collection('users2')
app = create_app('product')

from app.main import views

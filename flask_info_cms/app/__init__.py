from flask import Flask
from datetime import timedelta
from flask_pymongo import PyMongo
from config import config
from controller.dbmanager import ManagerDBMongo as MDB

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


# 初始化数据空连接：localhost 端口号：27017
MDB.init_db_client()
# 获取数据库列表
col_users = MDB.get_collection(db='mydatabase_test', col='users2')
col_ips = MDB.get_collection(db='mydatabase_test', col='available_ips')
col_ips2 = MDB.get_collection(db='mydatabase_test2', col='available_ips')

app = create_app('product')

from app.main import views

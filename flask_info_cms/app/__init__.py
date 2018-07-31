from flask import Flask
from flask_pymongo import PyMongo
from config import config
from controller.database import ManagerDBMongo

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    return app


ManagerDBMongo.init_db(db='mydatabase_test', col='users2')
col_users = ManagerDBMongo.get_collection('users2')
app = create_app('product')

from app.main import views

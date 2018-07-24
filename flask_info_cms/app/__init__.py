# Author: Jason Lu
from flask import Flask, request
# from flask.ext.pymongo import PyMongo
from flask_restful import Api, Resource
from flask_pymongo import PyMongo

app = Flask(__name__)
# 读取config
app.config.from_object('config')
# 数据库
app.config.update(
    MONGO_URI = 'mongodb://localhost:27017/mydatabase',
    MONGO_TEST_URI = 'mongodb://localhost:27017/test'
)

mongo = PyMongo(app)
# mongo_test = PyMongo(app, config_prefix = 'MONGO_TEST')

from app import views

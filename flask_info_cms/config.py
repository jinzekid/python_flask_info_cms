# Author: Jason Lu
# 全局配置文件，配置全局变量
#CSRF_ENABLED = True # 激活跨站点请求伪造保护
# 仅当CSRF激活的时候才需要，用来建立一个加密的令牌，用于验证一个表单
#SECRET_KEY = 'you-will-never-guess'


import os
from datetime import timedelta
from controller import database


basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    @staticmethod # 此注释可表明使用类名可以直接调用该方法
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    CSRF_ENABLED = True
    #MONGO_URI = 'mongodb://localhost:27017/dev_database'

class ProductionConfig(Config):
    CSRF_ENABLED = True
    #MONGO_URI = 'mongodb://localhost:27017/pro_database'


config = {
    'development': DevelopmentConfig,
    'product': ProductionConfig,

    'default': DevelopmentConfig
}


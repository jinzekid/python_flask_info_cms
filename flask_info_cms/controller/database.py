# Author: Jason Lu
import pymongo
from threading import Thread, Lock


class ManagerDBMongo(object):
    _instance_lock = Lock()  # 定义锁
    _ip = ''
    _port = 27017
    _db = ''
    _col = ''
    _client = []

    """
    单利模式的ManagerDBMongo
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(ManagerDBMongo, "_instance"):
            with ManagerDBMongo._instance_lock:
                if not hasattr(ManagerDBMongo, "_instance"):
                    ManagerDBMongo._instance = object.__new__(cls)

        return ManagerDBMongo._instance

    @classmethod
    def init_db(cls,
                ip='localhost',
                port=27017,
                db=None,
                col=None):
        """
        初始化数据库方法
        :param ip:
        :param port:
        :param db:
        :param col:
        :return:
        """
        cls._ip = ip
        cls._port = port
        cls._client = pymongo.MongoClient(cls._ip, cls._port)

        if db is None:
            return False

        if col is None:
            return False

        cls._db = cls._client[db]

        cls._col = cls._db[col]

        print(cls._db, cls._col)
        print(">>:finish init database")

        return True

    @classmethod
    def get_collection(cls, col):
        return cls._db[col]

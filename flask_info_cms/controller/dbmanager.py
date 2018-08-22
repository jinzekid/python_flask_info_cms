# Author: Jason Lu
import pymongo
from threading import Thread, Lock

class ManagerDBMongo(object):
    _instance_lock = Lock()  # 定义锁
    _ips = []
    _ports = [27017]
    _client = None

    """
    单利模式的ManagerDBMongo
    可以在多线程下使用
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(ManagerDBMongo, "_instance"):
            with ManagerDBMongo._instance_lock:
                if not hasattr(ManagerDBMongo, "_instance"):
                    ManagerDBMongo._instance = object.__new__(cls)

        return ManagerDBMongo._instance

    @classmethod
    def init_db_client(cls,
                ip='localhost',
                port=27017):
        """
        初始化数据库方法
        :param ip:
        :param port:
        :return:
        """

        # 加入ip列表
        if ip not in cls._ips:
            cls._ips.append(ip)

        # 加入端口列表
        if port not in cls._ports:
            cls._ports.append(port)

        client = pymongo.MongoClient(ip, port)
        if client:
            cls._client = client

        """ 
        if bool_new_ip:
            print(">>:client: %s" % cls._client )
            client = pymongo.MongoClient(ip, port)
            cls._client.append(client)
            #cls._client = client #.append({db: client})
        """

        print(">>:init_db: 成功" )
        print(">>:client: %s" % cls._client)

        return True


################################################################################
    """
    数据库基本操作
    """
    @classmethod
    def get_collection(cls, db=None, col=None):
        """
        获取数据库集合
        :param cls:
        :param db:
        :param col:
        :return:
        """
        if db is None or col is None:
            print(">>:get_collection err: db or col is None")
            return

        if cls._client is None:
            print(">>:get_collection err: cls._client is None")
            return

        return cls._client[db][col]

    @classmethod
    def get_data(cls, col):
        pass

    @classmethod
    def add_data(cls, db=None, col=None, data=None):
        """
        新增记录
        :param cls:
        :param db:
        :param col:
        :param data:
        :return:
        """
        if data is None or db is None or col is None:
            print(">>:add_data err")
            return

        pass

    @classmethod
    def del_data(cls, db=None, col=None, data=None):
        """
        删除匹配记录
        :param cls:
        :param db:
        :param col:
        :param data:
        :return:
        """
        if data is None or db is None or col is None:
            print(">>:del_data err")
            return


        pass

    @classmethod
    def update_date(cls, db=None, col=None, data=None):
        """
        更新记录信息
        :param cls:
        :param db:
        :param col:
        :param data:
        :return:
        """
        if data is None or db is None or col is None:
            print(">>:update_date err")
            return
        pass

    @classmethod
    def search_data(cls, db=None, col=None, data=None):
        """
        搜索记录
        :param db:
        :param col:
        :param data:
        :return:
        """
        if data is None or db is None or col is None:
            print(">>:search_data err")
            return

        pass






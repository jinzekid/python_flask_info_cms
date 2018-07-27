# Author: Jason Lu
from app import col_users


class UserController(object):
    @classmethod
    def get_users(cls, filter=0, name=None):
        """
        :param filter: 过滤方式，0：全部记录返回，1：特定查询，根据后面参数内容
        :param name: 过滤需要查找的用户姓名
        :return: 查找，404：未查找到用户记录，users：用户列表
        """
        users = col_users#mongo.db.users

        list_users = []
        if filter == 0:
            print(">>:search user controller...")
            rows = users.find(
                {},
                {'_id': 0, 'username': 1, 'password': 1}
            )
            for row in rows:
                list_users.append(row)

            return {'code': 1, 'users': list_users}

        if name is not None:
            someone = users.find_one(
                {'username': name},
                {'_id': 0, 'username': 1, 'password': 1}
            )

        if someone is None:
            return {'code': 404}

        list_users.append(someone)
        return {'code': 1, 'users': list_users}

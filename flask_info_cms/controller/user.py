# Author: Jason Lu
from flask import jsonify
from app import app, mongo


class UserController(object):
    @classmethod
    def get_users(cls, filter=0, name=None):
        user = mongo.db.users

        list_users = []
        print('>>:filter:%s'%str(filter))
        if filter == 0:
            print(">>:search user controller...")
            rows = user.find({},{'_id':0, 'username':1, 'password':1})
            for row in rows:
                print(row)
                list_users.append(row)

            return {'code':1, 'users':list_users}


        if name is not None:
            someone = user.find_one({
                'username': name
            },{'_id':0, 'username':1, 'password': 1})

        if someone is None:
            return {'code': 404}

        list_users.append(someone)
        return {'code':1, 'users':list_users}

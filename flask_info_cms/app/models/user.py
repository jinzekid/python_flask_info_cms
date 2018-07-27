# Author: Jason Lu
"""
from app import mongo
from models.device import Device1

class User(mongo.Document):
    name = mongo.StringField(max_length=30, required=True)
    password = mongo.StringField(max_length=30, min_length=6, required=True)
    phone = mongo.StringField()
    device = mongo.ReferenceField(Device1)
    devices = mongo.ListField(mongo.ReferenceField(Device1))
    emdevices = mongo.ListField(mongo.EmbeddedDocumentField('Device1'))

    def __str__(self):
        return "name:%s - phone:%s"%(self.name, self.phone)
"""

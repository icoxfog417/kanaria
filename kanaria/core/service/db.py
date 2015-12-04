import re
import inspect
from pymongo import MongoClient


class MongoDBService(object):
    ID_FIELD = "_id"
    KEY_FUNC = "unique_key"

    def __init__(self, db_uri=""):
        self.client = MongoClient(db_uri if db_uri else "mongodb://localhost:27017/default")

    def get_collection(self, cls_or_instance):
        database = self.client.get_default_database()
        collection = self.get_collection_name(cls_or_instance)
        return database[collection]

    def save(self, instance):
        collection = self.get_collection(instance)
        _id = None

        if hasattr(instance, self.ID_FIELD) and getattr(instance, self.ID_FIELD):
            _id = instance._id
        elif hasattr(instance, self.KEY_FUNC):
            key = getattr(instance, self.KEY_FUNC)()
            same = collection.find_one({self.KEY_FUNC: key})
            if same:
                _id = same._id

        instance_dic = self.object_to_dict(instance)
        if _id:
            collection.update_one({"_id": _id}, instance_dic)
        else:
            collection.insert_one(instance_dic)

    @classmethod
    def object_to_dict(cls, instance):
        dic = {}
        for a in inspect.getmembers(instance, lambda a: not inspect.isroutine(a)):
            if not a[0].startswith("_"):
                dic[a[0]] = a[1]

        if hasattr(instance, cls.ID_FIELD) and instance._id:
            dic[cls.ID_FIELD] = instance._id
        if hasattr(instance, cls.KEY_FUNC):
            key = getattr(instance, cls.KEY_FUNC)()
            if key:
                dic[cls.KEY_FUNC] = key

        return dic

    @classmethod
    def get_collection_name(cls, cls_or_instance):
        cls_name = ""
        if type(cls_or_instance) is type:
            cls_name = cls_or_instance.__name__
        else:
            cls_name = type(cls_or_instance).__name__

        collection_name = cls.__camel_to_snake(cls_name)
        return collection_name

    @classmethod
    def __camel_to_snake(cls, name):
        n1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)  # Ab -> A_b
        n2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', n1)  # aB -> a_B
        n3 = n2.lower()  # A_b & a_B -> a_b & a_b
        return n3

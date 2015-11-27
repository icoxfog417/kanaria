import unittest
from datetime import datetime
from kanaria.core.service.db import MongoDBService


class ModelExample(object):

    def __init__(self, title="", description="", date=None):
        self.title = title
        self.description = description
        self.date = date if date else datetime.now()
        self._private = False

    def method(self):
        pass

class TestDBService(unittest.TestCase):

    def test_serialize(self):
        db = MongoDBService()
        m = ModelExample("test", "test_serialize")

        name = db.get_collection_name(m)
        dic = db.object_to_dict(m)

        self.assertTrue("model_example", name)
        self.assertTrue(m.title, dic["title"])
        self.assertTrue(m.date, dic["date"])
        self.assertFalse("_private" in dic)
        self.assertFalse("method" in dic)

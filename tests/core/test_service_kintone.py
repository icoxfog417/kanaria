import unittest
from kanaria.core.service.kintone import kintoneInterface


class TestServiceKintone(unittest.TestCase):

    def test_create_kanaria(self):
        kintone = kintoneInterface()
        kanaria = kintone.get_kanaria(True)
        self.assertTrue(kanaria)

    def test_get_application(self):
        kintone = kintoneInterface()
        app = kintone.get_application_by_code("xxxx")
        print(app)
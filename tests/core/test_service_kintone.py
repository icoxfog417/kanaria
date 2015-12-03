import unittest
from kanaria.core.service.kintone import kintoneInterface


class TestServiceKintone(unittest.TestCase):

    def test_create_kanaria(self):
        kintone = kintoneInterface()
        kanaria = kintone.get_kanaria(True)
        self.assertTrue(kanaria)

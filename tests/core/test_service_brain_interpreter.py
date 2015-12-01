import unittest

from kanaria.core.service.brain.interpreter import extract_application_name


class TestInterpreter(unittest.TestCase):

    def test_extract_application_name(self):
        sents = ['クレーム管理がしたい', '日報管理がしたい', '勉強会の資料を管理したい',
                 '', 'なんでやねん', 'resource management']
        self.assertEqual(extract_application_name(sents[0]), 'クレーム管理')
        self.assertEqual(extract_application_name(sents[1]), '日報管理')
        self.assertEqual(extract_application_name(sents[2]), '勉強会資料管理')
        self.assertEqual(extract_application_name(sents[3]), '')
        self.assertEqual(extract_application_name(sents[4]), '')
        self.assertEqual(extract_application_name(sents[5]), 'resourcemanagement')
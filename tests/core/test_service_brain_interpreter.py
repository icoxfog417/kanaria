import unittest
import kanaria.core.service.brain.interpreter as inp
from kanaria.core.service.brain.mind_types import OrderType


class TestInterpreter(unittest.TestCase):

    def test_extract_application_name(self):
        sents = ['クレーム管理がしたい', '日報管理がしたい', '勉強会の資料を管理したい',
                 '', 'なんでやねん', 'resource management']
        self.assertEqual(inp.extract_application_name(sents[0]), 'クレーム管理')
        self.assertEqual(inp.extract_application_name(sents[1]), '日報管理')
        self.assertEqual(inp.extract_application_name(sents[2]), '勉強会資料管理')
        self.assertEqual(inp.extract_application_name(sents[3]), '')
        self.assertEqual(inp.extract_application_name(sents[4]), '')
        self.assertEqual(inp.extract_application_name(sents[5]), 'resourcemanagement')

    def test_interpret_operation(self):
        target_name, operation_type = inp.interpret_operation("報告日を追加してほしい")
        self.assertEqual("報告日", target_name)
        self.assertEqual(OrderType.ADD_ITEM, operation_type)

        target_name, operation_type = inp.interpret_operation("電話番号は削除してほしい")
        self.assertEqual("電話番号", target_name)
        self.assertEqual(OrderType.DELETE_ITEM, operation_type)

        target_name, operation_type = inp.interpret_operation("管理用の日付を入れてほしい")
        self.assertEqual("管理用日付", target_name)
        self.assertEqual(OrderType.ADD_ITEM, operation_type)

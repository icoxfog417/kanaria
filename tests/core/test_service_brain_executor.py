# -*- coding: utf-8 -*-
import unittest
from kanaria.core.service.brain.mind_types import OrderType, DecisionType
import kanaria.core.service.brain.executor as executor
from kanaria.core.model.letter import Letter
from kanaria.core.model.order import Order
from kanaria.core.model.action import Action


class TestServiceBrainExecutorWithApp(unittest.TestCase):
    TEST_APP = None

    @classmethod
    def setUpClass(cls):
        """
        letter = Letter("クレームの管理をしたい", "")
        order = Order(OrderType.CREATE_APPLICATION, "test_service_brain_executor", letter.subject, target="クレーム管理", letter=letter)
        action = Action(DecisionType.EXECUTE, order)
        copied = executor.create_application(action)
        """
        from kanaria.core.environment import Environment
        cls.TEST_APP = Environment.get_kintone_service().app(app_id=268)
        print("Caution: You have to delete application on kintone!")

    @classmethod
    def tearDownClass(cls):
        print("Caution: You have to delete application on kintone!")
        cls.TEST_APP = None

    def test_post_letter(self):
        body = """
        2015/1/1

        本日お客様から、掃除したはずなのにサッシに埃がついているじゃないとクレームがありました。
        現場に行ってみてみると、確かにまだ汚れがありました。

        お客様連絡先
        0322221111
        """

        letter = Letter("", body)
        order = Order(OrderType.POST_LETTER, "test_user", app_id=self.TEST_APP.app_id, letter=letter)
        action = Action(DecisionType.EXECUTE, order)

        result = executor.post(action)
        self.assertTrue(result.ok)

    def test_update_item(self):
        letter = Letter("報告日を追加してほしい", "")
        order = Order(OrderType.ADD_ITEM, "test_user", app_id=self.TEST_APP.app_id, letter=letter)
        order.target = "報告日"
        action = Action(DecisionType.EXECUTE, order)

        result = executor.update_application(action)
        self.assertTrue(result.ok)

        order.order_type_text = OrderType.DELETE_ITEM.value
        result = executor.update_application(action)
        self.assertTrue(result.ok)

    def test_make_reply(self):
        from kanaria.core.environment import Environment
        from kanaria.core.service.brain import Brain

        env = Environment()
        domain = env.mail_domain
        kanaria_admin = Brain.MY_USER_NAME + "@" + domain
        from_address = "test_user@" + domain
        letter = Letter("報告日を追加してほしい", "", from_address=from_address, to_addresses=kanaria_admin)
        order = Order(OrderType.ADD_ITEM, "test_user", app_id=self.TEST_APP.app_id, letter=letter)
        action = Action(DecisionType.EXECUTE, order)

        reply = action.make_reply(message="返信を書きました")
        self.assertTrue(reply.subject)
        self.assertTrue(from_address in reply.to_addresses)

        # system mail
        letter.from_address = kanaria_admin
        letter.to_addresses = [kanaria_admin, from_address]
        reply = action.make_reply(message="管理者から返信を書きました")
        self.assertTrue(kanaria_admin not in reply.to_addresses)

    def create_order(self, order_type, subject, body=""):
        from kanaria.core.model.letter import Letter
        from kanaria.core.model.order import Order

        letter = Letter(subject, body)
        order = Order(order_type, "test_service_brain_executor", subject, letter=letter)
        return order

# -*- coding: utf-8 -*-
import unittest
from kanaria.core.service.brain.mind_types import OrderType, DecisionType
import kanaria.core.service.brain.executor as executor
from kanaria.core.model.action import Action


class TestServiceBrainExecutor(unittest.TestCase):

    def test_create_application(self):
        print("Caution: You have to delete application on kintone!")
        order = self.create_order(OrderType.CREATE_APPLICATION, "クレームの管理をしたい")
        order.target = "クレーム管理"
        action = Action(DecisionType.EXECUTE, order)

        copied = executor.create_application(action)
        self.assertTrue(copied)
        default = executor.create_application(action, enable_copy=False)
        self.assertTrue(default)

    def create_order(self, order_type, subject, body=""):
        from kanaria.core.model.letter import Letter
        from kanaria.core.model.order import Order

        letter = Letter(subject, body)
        order = Order(order_type, "test_service_brain_executor", subject, letter=letter)
        return order

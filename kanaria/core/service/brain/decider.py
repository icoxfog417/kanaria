# -*- coding: utf-8 -*-
from kanaria.core.service.kintone import kintoneInterface
from kanaria.core.service.brain.mind_types import OrderType, DecisionType
from kanaria.core.model.order import Order
from kanaria.core.model.action import Action


def decide(order):
    decision_type = DecisionType.IGNORE
    o = order
    message = ""

    if order.order_type() == OrderType.CREATE_APPLICATION:
        kintone = kintoneInterface()
        infos = kintone.find_similar_applications(order.target)
        if len(infos) > 0:
            decision_type = DecisionType.HOLD
            Order.hold_order(o)
            names = [info.name for info in infos][:2]
            message = "{0}などの似ているアプリケーションがありますがよろしいですか？".format("、".join(names))
        else:
            decision_type = DecisionType.EXECUTE
    elif order.order_type() == OrderType.ALLOW:
        o = Order.pop_order(order.user_address)
        decision_type = DecisionType.EXECUTE
    else:
        if order.app_id:
            decision_type = DecisionType.EXECUTE
        else:
            message = "このアドレスで登録されているアプリケーションが見つかりません。"

    a = Action(decision_type, o, message)
    return a

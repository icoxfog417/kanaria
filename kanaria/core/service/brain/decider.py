# -*- coding: utf-8 -*-
import kanaria.core.service.kintone as kintone
from kanaria.core.service.brain.mind_types import OrderType, DecisionType
from kanaria.core.model.order import Order
from kanaria.core.model.action import Action


def decide(order):
    decision_type = DecisionType.IGNORE
    o = order
    message = ""

    if order.order_type() == OrderType.CREATE_APPLICATION:
        infos = kintone.find_similar_applications(order.target)
        if len(infos) > 0:
            decision_type = DecisionType.HOLD
            names = [info.name for info in infos][:2]
            message = "{0}などの似ているアプリケーションがありますがよろしいですか？".format("、".join(names))
        else:
            decision_type = DecisionType.EXECUTE
    elif order.order_type() == OrderType.ALLOW:
        o = Order.get_order(order.user_address)
        decision_type = DecisionType.EXECUTE
    else:
        # not consider yet
        decision_type = DecisionType.EXECUTE

    a = Action(decision_type, o, message)
    return a

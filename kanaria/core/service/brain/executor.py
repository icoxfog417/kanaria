# -*- coding: utf-8 -*-
import re
import kanaria.core.service.kintone as kintone
from kanaria.core.service.brain.mind_types import OrderType, DecisionType
from kanaria.core.model.order import Order
from kanaria.core.environment import Environment


def execute(action):
    if action.decision_type() == DecisionType.IGNORE:
        return None
    elif action.decision_type() == DecisionType.HOLD:
        Order.hold_order(action.order)
    else:
        if action.order.order.order_type() == OrderType.CREATE_APPLICATION:
            app = create_application(action)
            app.create(action.order.letter())  # first record for new application
        elif action.order.order_type() == OrderType.POST_LETTER:
            post(action)
        else:
            update_application(action)


def create_application(action):
    code = _generate_code(action.order.target)
    # todo: choose application template and copy it.
    app = kintone.create_default_application(action.order.target, code)
    return app


def _generate_code(name):
    return "application code"


def update_application(action):
    app_id = action.order.app_id
    field_name = action.order.target
    pass


def post(action):
    ks = Environment.get_kintone_service()
    app = ks.app(action.order.app_id)
    letter = action.order.letter()
    return app.create(letter)


def make_reply(self, letter):
    return None


def decide_type_from_name(self, text):
    field_type = "SINGLE_LINE_TEXT"

    if re.search(".+(日|日付)$"):
        field_type = "DATE"
    elif re.search(".+(時刻|時間)$"):
        field_type = "DATETIME"
    elif re.search(".+(リンク|URL)$"):
        field_type = "LINK"
    elif re.search(".+(ファイル|写真)$"):
        field_type = "FILE"
    elif len(text.split(",")) > 0:
        field_type = "CHECK_BOX"

    return field_type


def decide_type_from_format(self, value):
    pass

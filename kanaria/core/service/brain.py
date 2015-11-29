# -*- coding: utf-8 -*-
import re
from enum import Enum
from janome.tokenizer import Tokenizer
import kanaria.core.service.kintone as kintone
from kanaria.core.service.mind_types import OrderType, DecisionType
from kanaria.core.model.letter import Letter
from kanaria.core.model.order import Order
from kanaria.core.environment import Environment


class Brain(object):
    MY_NAME = "カナリア"
    MY_USER_NAME = "kanaria_administrator"

    def __init__(self):
        pass

    def understand_order(self, letter):
        order_type = OrderType.NONE
        app_id = ""
        target = ""

        if letter.to_includes(self.MY_USER_NAME):
            if letter.subject:
                order_type = OrderType.CREATE_APPLICATION
                target = self.extract_name(letter.subject)
        else:
            # to application address
            # get app_id
            for a in letter.to_address:
                app = kintone.get_application(Letter.get_user(a))
                if app:
                    app_id = app.app_id

            # get order type
            if letter.subject:
                order_type, target = self.interpret_order(letter.subject)
            else:
                order_type = OrderType.POST_LETTER

        o = Order(letter.from_address, letter.subject, order_type, target)
        return o

    def interpret_order(self, order_text):
        # todo: implements how to interpret order from text
        return OrderType.ADD_ITEM, "field_name"

    def decide_action(self, order):
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
        else:
            # not consider yet
            decision_type = DecisionType.EXECUTE

        a = Action(decision_type, o, message)
        return a

    def extract_name(self, subject):
        # todo: implements how to create application name and code from subject
        return "name"

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

    @classmethod
    def trim(cls, text):
        t = text.strip().replace("\r", "").replace("\n", "")
        return t

    @classmethod
    def split(cls, text):
        lines = text.split("\n")
        lines = [cls.trim(ln) for ln in lines]
        return lines


class Action(object):

    def __init__(self, decision_type, order, message):
        self.decision_type = decision_type
        self.order = order
        self.message = message

    def execute(self, letter):
        if self.decision_type == DecisionType.IGNORE:
            return None
        elif self.decision_type == DecisionType.HOLD:
            Order.hold_order(self.order)
        else:
            if self.order.order_type() == OrderType.CREATE_APPLICATION:
                app = self.create_application()
                app.create(letter)  # first record for new application
            elif self.order.order_type() == OrderType.POST_LETTER:
                self.post(letter)
            else:
                self.update_application()

    def create_application(self):
        code = self.generate_code(self.order.target)
        app = kintone.create_default_application(self.order.target, code)
        return app

    @classmethod
    def generate_code(cls, name):
        return "application code"

    def update_application(self):
        app_id = self.order.app_id
        field_name = self.order.target
        pass

    def post(self, letter):
        ks = Environment.get_kintone_service()
        app = ks.app(self.order.app_id)
        return app.create(letter)

    def make_reply(self, letter):
        return None

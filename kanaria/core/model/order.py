from kanaria.core.service.brain.mind_types import OrderType
from kanaria.core.environment import Environment
from kanaria.core.model.letter import Letter


class Order(object):

    def __init__(self, order_type_text, user_address, subject, app_id="", target="", letter=None):
        self._id = None
        self.order_type_text = ""
        self.user_address = user_address
        self.subject = subject
        self.app_id = app_id
        self.target = ""
        self.letter_id = ""
        self._letter = letter

        text = order_type_text
        if isinstance(order_type_text, OrderType):
            text = order_type_text.value
        self.order_type_text = text

    def order_type(self):
        return OrderType(self.order_type_text)

    def letter(self):
        lt = None
        if self._letter:
            lt = self._letter
        elif self.letter_id:
            from kanaria.core.service.kintone import get_kanaria
            app = get_kanaria()
            if app:
                self._letter = app.get(self.letter_id).model(Letter)
                lt = self._letter
        return lt

    @classmethod
    def deserialize(cls, order_dic):
        instance = Order(
            order_dic["order_type_text"],
            order_dic["user_address"],
            order_dic["subject"],
            app_id=order_dic["app_id"],
            target=order_dic["target"]
        )
        instance._id = order_dic["_id"]
        instance.letter_id = order_dic["letter_id"]
        return instance

    @classmethod
    def hold_order(cls, order):
        db = Environment.get_db()
        # delete previous held orders
        db.get_collection(Order).delete_many({"user_address": order.user_address})
        db.save(order)

    @classmethod
    def get_order(cls, user_address):
        db = Environment.get_db()
        order_dic = db.get_collection(Order).find_one({"user_address": user_address})
        order = cls.deserialize(order_dic)
        return order

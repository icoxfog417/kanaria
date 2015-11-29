from kanaria.core.service.mind_types import OrderType
from kanaria.core.environment import Environment


class Order(object):

    def __init__(self, user_address, subject, order_type_text, app_id="", target=""):
        self._id = None
        self.user_address = user_address
        self.subject = subject
        self.order_type_text = ""
        self.app_id = app_id
        self.target = ""

        text = order_type_text
        if isinstance(order_type_text, OrderType):
            text = order_type_text.value

        self.order_type_text = text

    @classmethod
    def deserialize(cls, order_dic):
        instance = Order(
            order_dic["user_address"],
            order_dic["subject"],
            order_dic["order_type_text"],
            order_dic["app_id"],
            order_dic["target"]
        )
        instance._id = order_dic["_id"]
        return instance

    def order_type(self):
        return OrderType(self.order_type_text)

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

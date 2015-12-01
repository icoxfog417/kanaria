from kanaria.core.service.brain.mind_types import DecisionType


class Action(object):

    def __init__(self, decision_type_text, order, message=""):
        self.decision_type_text = ""
        self.order = order
        self.message = message

        text = decision_type_text
        if isinstance(decision_type_text, DecisionType):
            text = decision_type_text.value
        self.decision_type_text = text

    def decision_type(self):
        return DecisionType(self.decision_type_text)

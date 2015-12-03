from kanaria.core.service.brain.mind_types import DecisionType
from kanaria.core.environment import Environment
from kanaria.core.service.brain import Brain
from kanaria.core.model.letter import Letter


class Action(object):

    def __init__(self, decision_type_text, order, message=""):
        self.decision_type_text = ""
        self.order = order
        self.message = message

        text = decision_type_text
        if isinstance(decision_type_text, DecisionType):
            text = decision_type_text.value
        self.decision_type_text = text

    def make_reply(self, subject="", message="", from_user=""):
        msg = message if message else self.message
        if not msg:
            return None

        sub = subject if subject else "Re: " + self.order.letter().subject
        env = Environment()
        letter = self.order.letter()
        admin_address = Brain.MY_USER_NAME + "@" + env.mail_domain
        from_address = from_user + "@" + env.mail_domain if from_user else admin_address
        to_address = [a for a in letter.to_address if a not in [admin_address, from_address]]
        letter = Letter(subject=sub, body=msg, from_address=from_address, to_addresses=to_address)
        return letter

    def decision_type(self):
        return DecisionType(self.decision_type_text)

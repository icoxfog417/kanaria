from kanaria.core.service.brain import Brain


class Agent(object):

    def __init__(self):
        pass

    def accept(self, letter):
        brain = Brain()

        order = brain.understand_order(letter)
        action = brain.decide_action(order)

        if action:
            action.execute(letter)

        reply = action.make_reply(letter)
        return reply


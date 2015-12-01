import kanaria.core.service.brain.interpreter as interpreter
import kanaria.core.service.brain.decider as decider
import kanaria.core.service.brain.executor as executor
from kanaria.core.service.kintone import get_kanaria


class Agent(object):

    def __init__(self):
        get_kanaria(create_if_not_exist=True)

    def accept(self, letter):
        order = interpreter.interpret(letter)
        action = decider.decide(order)
        result = executor.execute(action)

        reply = None
        if result:
            reply = result.make_reply()
        return reply

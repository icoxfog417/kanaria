# -*- coding: utf-8 -*-
from janome.tokenizer import Tokenizer
import kanaria.core.service.kintone as kintone
from kanaria.core.service.brain import Brain
from kanaria.core.service.brain.mind_types import OrderType
from kanaria.core.model.letter import Letter
from kanaria.core.model.order import Order


def interpret(letter):
    order_type = OrderType.NONE
    app_id = ""
    target = ""
    kanaria = kintone.get_kanaria()

    if letter.to_includes(Brain.MY_USER_NAME):
        # to kanaria administrator
        if kanaria:
            app_id =kanaria.app_id

        if letter.subject:
            order_type = OrderType.CREATE_APPLICATION
            target = extract_application_name(letter.subject)
    else:
        # to application's address
        for a in letter.to_address:
            app = kintone.get_application(Letter.get_user(a))
            if app:
                app_id = app.app_id

        # get order type
        if letter.subject:
            target, order_type = interpret_operation(letter.subject)
        else:
            order_type = OrderType.POST_LETTER

    o = Order(order_type, letter.from_address, letter.subject, app_id=app_id, target=target, letter=letter)
    # post letter to kanaria
    if kanaria:
        created = kanaria.create(letter)
        o.letter_id = created.record_id

    return o


def extract_application_name(text):
    t = Tokenizer()
    tokens = t.tokenize(text)
    words = []
    for token in tokens:
        pos = token.part_of_speech.split(',')
        if pos[0] == '名詞':
            words.append(token.surface)
    return ''.join(words)


def interpret_operation(text):
    # todo: implements how to interpret order from text
    return "field_name", OrderType.ADD_ITEM


def interpret_content(letter):
    pass

# -*- coding: utf-8 -*-
import re
from janome.tokenizer import Tokenizer
from kanaria.core.service.kintone import kintoneInterface
from kanaria.core.service.brain import Brain
from kanaria.core.service.brain.mind_types import OrderType
from kanaria.core.model.letter import Letter
from kanaria.core.model.order import Order


def interpret(letter):
    kintone = kintoneInterface()
    order_type = OrderType.NONE
    app_id = ""
    target = ""
    kanaria = kintone.get_kanaria()

    if letter.to_includes(Brain.MY_USER_NAME):
        # to kanaria administrator
        if kanaria:
            app_id =kanaria.app_id

        if letter.subject:
            order_type = interpret_allow(letter.subject)
            if order_type != OrderType.ALLOW:
                order_type = OrderType.CREATE_APPLICATION
                target = extract_application_name(letter.subject)
    else:
        # to application's address
        for a in letter.to_addresses:
            app = kintone.get_application_by_code(Letter.get_user(a))
            if app:
                app_id = app.app_id

        # get order type
        if app_id:
            if letter.subject:
                target, order_type = interpret_operation(letter.subject)
            else:
                order_type = OrderType.POST_LETTER

    o = Order(order_type, letter.from_address, app_id=app_id, target=target, letter=letter)
    # post letter to kanaria
    if kanaria:
        # todo have to support attached file
        if len(letter.attached_files) == 0:
            created = kanaria.create(letter)
            o.letter_id = created.record_id

    return o


def extract_application_name(text):
    words = []
    for t in _tokenize(text):
        if t.pos[0] == "名詞":
            words.append(t.surface)
    return "".join(words)


def interpret_allow(text):
    pattern_for_allow = re.compile(r"OK|いいよ")
    if pattern_for_allow.search(text.strip()):
        return OrderType.ALLOW
    else:
        return OrderType.NONE


def interpret_operation(text):
    operation_type = OrderType.NONE
    pattern_for_add = re.compile(r"追加|入れ")
    pattern_for_del = re.compile(r"削除|消し")

    if interpret_allow(text) == OrderType.ALLOW:
        return "", OrderType.ALLOW

    targets = []
    operations = []
    target_part = True
    for t in _tokenize(text):
        if t.pos[0] == "助詞" and t.pos[1] in ["格助詞", "係助詞", "副助詞"]:
            target_part = False
            continue
        else:
            array = targets if target_part else operations
            if t.pos[0] == "名詞":
                array.append(t.surface)
            elif not target_part and t.pos[0] == "動詞":
                array.append(t.surface)

    target = "".join(targets)
    operation = "".join(operations)

    if pattern_for_add.search(operation):
        operation_type = OrderType.ADD_ITEM
    elif pattern_for_del.search(operation):
        operation_type = OrderType.DELETE_ITEM

    return target, operation_type


def _tokenize(text):
    from collections import namedtuple
    Token = namedtuple("Token", ["t", "surface", "pos"])

    t = Tokenizer()
    tokens = t.tokenize(text)
    for t in tokens:
        nt = Token(t, t.surface, t.part_of_speech.split(","))
        yield nt

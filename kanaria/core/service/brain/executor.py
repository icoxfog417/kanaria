# -*- coding: utf-8 -*-
import re
from datetime import datetime
from enum import Enum
from collections import namedtuple
from itertools import chain
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
        if action.order.order_type() == OrderType.CREATE_APPLICATION:
            app = create_application(action)
            app.create(action.order.letter())  # first record for new application
        elif action.order.order_type() == OrderType.POST_LETTER:
            post(action)
        else:
            update_application(action)


def create_application(action, enable_copy=True):
    name = action.order.target
    code = Environment.get_translator().translate(name, "en").replace(" ", "_")

    app_info = kintone.find_similar_applications(name, find_template=True)

    app = None
    if len(app_info) > 0 and enable_copy:
        app = kintone.copy_application(app_info[0].app_id, name, code)
    else:
        app = kintone.create_default_application(name, code)

    return app


def update_application(action):
    app_id = action.order.app_id
    field_name = action.order.target
    pass


def post(action):
    ks = Environment.get_kintone_service()
    app = ks.app(action.order.app_id)
    letter = action.order.letter()

    # get form structure
    fields = app.administration().form().get(app.app_id).fields
    data = map_letter_to_field(letter, fields)

    # file field
    file_field = [f for f in fields if f.field_type == "FILE"]
    if len(file_field) > 0 and len(letter.attached_files) > 0:
        from pykintone.structure_field import File
        f = File.upload(letter.attached_files[0], app)
        data[file_field[0].code] = {
            "value": {
                "fileKey": f.file_key
            }
        }

    result = app.create(data)
    return result


def make_reply(letter):
    return None


def map_letter_to_field(letter, fields, app=None):
    from pykintone.account import kintoneService
    Matcher = namedtuple("Matcher", ["field_type", "data_type", "pattern"])
    separator = BlockSeparator()

    data = {}
    # todo: have to think more intelligent way
    blocks = separator.split_by_blank_line(letter.body)
    blocks = list(chain.from_iterable([separator.split_by_data_type(b.value) for b in blocks]))

    def get_blocks(bs, dtype):
        _bs = [b for b in bs if b.data_type == dtype]
        _bs = [b for b in _bs if not b.name]
        return _bs

    def get_fields(fs, ftype, ptn=None):
        _fs = []
        if isinstance(ftype, (list, tuple)):
            _fs = [f for f in fs if f.field_type in ftype]
        else:
            _fs = [f for f in fs if f.field_type == ftype]

        if ptn:
            _fs = [f for f in _fs if ptn.search(f.label)]
        _fs = [f for f in _fs if f.code not in data]
        return _fs

    match_types = [
        Matcher(["SINGLE_LINE_TEXT"], DataType.MAIL, re.compile(r"(メール|アドレス|mail|address)")),
        Matcher(["SINGLE_LINE_TEXT"], DataType.PHONE, re.compile(r"(電話|tel)")),
        Matcher(["DATE", "DATETIME"], DataType.DATE, None),
        Matcher(["SINGLE_LINE_TEXT", "MULTI_LINE_TEXT", "RICH_TEXT"], "", None),
    ]

    for m in match_types:
        fs = get_fields(fields, m.field_type, m.pattern)
        bs = get_blocks(blocks, m.data_type)

        for i, f in enumerate(fs):
            if i >= len(bs):
                break
            v = bs[i].value
            if m.data_type == DataType.DATE:
                # check year existence
                v = v.replace("/", "-")
                if len(v.split("-")) < 2:
                    v = str(datetime.now().year) + "-" + v

            data[f.code] = {
                "value": v
            }
            bs[i].name = f.code

    return data


def decide_type_from_format(self, value):
    pass


class DataType(Enum):
    MAIL = "MAIL"
    PHONE = "PHONE"
    DATE = "DATE"


class Field(object):

    def __init__(self, value="", data_type=""):
        self.value = value
        self.data_type = data_type
        self.name = ""


class BlockSeparator(object):

    def __init__(self):
        self.pattern_date = re.compile(r"(\d{4}/)?[0-1]?\d/[0-3]?\d", flags=re.ASCII)
        self.pattern_phone = re.compile(r"(\d{2,3}-?\d{4}-?\d{4})", flags=re.ASCII)
        self.pattern_mail = re.compile(r"[A-Za-z0-9][A-Za-z0-9_\-\.]*@[A-Za-z0-9][A-Za-z0-9_\-]+?(\.[A-Za-z0-9_\-\.]+)+?", flags=re.ASCII)

    def split_by_blank_line(self, text):
        lines = self._strip_split(text)
        blocks = []
        b = []
        for ln in lines:
            _ln = self._trim(ln)
            if not _ln:
                if len(b) > 0:
                    blocks.append("\n".join(b))
                    b = []
            else:
                b.append(ln)
        else:
            if not self._blank_array(b):
                blocks.append("\n".join(b))

        fields = [self.make_field(b) for b in blocks]
        return fields

    def split_by_data_type(self, text):
        lines = self._strip_split(text)

        fields = []
        remain = []
        remain_index = -1
        for i, ln in enumerate(lines):
            f = self.make_field(ln)
            if f.data_type:
                fields.append(f)
            else:
                remain.append(ln)
                if remain_index < 0:
                    remain_index = i

        if remain_index > -1:
            fields.insert(remain_index, self.make_field("\n".join(remain)))

        return fields

    @classmethod
    def _strip_split(cls, text, separator="\n"):
        return text.strip().split(separator)

    @classmethod
    def _trim(cls, text):
        return text.strip().replace("\r", "").replace("\n", "")

    @classmethod
    def _blank_array(cls, arr):
        v = "".join([cls._trim(a) for a in arr])
        return True if not v else False

    def make_field(self, value):
        data_type = ""
        _v = self._trim(value)
        match_strict = lambda p, t: p.match(t) and p.match(t).end() == len(t)
        if match_strict(self.pattern_date, _v):
            data_type = DataType.DATE
        elif match_strict(self.pattern_phone, _v):
            data_type = DataType.PHONE
        elif match_strict(self.pattern_mail, _v):
            data_type = DataType.MAIL
        else:
            _v = value

        f = Field(value=_v, data_type=data_type)
        return f

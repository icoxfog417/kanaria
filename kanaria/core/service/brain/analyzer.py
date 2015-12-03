import re
from enum import Enum
from collections import namedtuple
from datetime import datetime
from itertools import chain


class DataType(Enum):
    MAIL = "MAIL"
    PHONE = "PHONE"
    DATE = "DATE"


class Field(object):

    def __init__(self, value="", data_type=""):
        self.value = value
        self.data_type = data_type
        self.name = ""


class TextAnalyzer(object):

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

    def map_letter_to_field(self, letter, fields, app=None):
        Matcher = namedtuple("Matcher", ["field_type", "data_type", "pattern"])

        data = {}
        # todo: have to think more intelligent way
        blocks = self.split_by_blank_line(letter.body)
        blocks = list(chain.from_iterable([self.split_by_data_type(b.value) for b in blocks]))

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

    def estimate_field_type(self, text):
        field_type = "SINGLE_LINE_TEXT"

        if re.search(r".+(日|日付)$", text):
            field_type = "DATE"
        elif re.search(r".+(時刻|時間)$", text):
            field_type = "TIME_STAMP"
        elif re.search(r".+(リンク|URL)$", text):
            field_type = "LINK"
        elif re.search(r".+(ファイル|写真)$", text):
            field_type = "FILE"

        return field_type

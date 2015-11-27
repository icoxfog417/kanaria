# -*- coding: utf-8 -*-
import re
from janome.tokenizer import Tokenizer


class Brain(object):

    def __init__(self):
        pass

    def get_type_from_text(self, text):
        field_type = "SINGLE_LINE_TEXT"

        if re.search(".+(日|日付)$"):
            field_type = "DATE"
        elif re.search(".+(時刻|時間)$"):
            field_type = "DATETIME"
        elif re.search(".+(リンク|URL)$"):
            field_type = "LINK"
        elif re.search(".+(ファイル|写真)$"):
            field_type = "FILE"
        elif len(text.split(",")) > 0:
            field_type = "CHECK_BOX"

        return field_type

    def get_type_from_value(self, value):
        from datetime import datetime

        field_type = "SINGLE_LINE_TEXT"
        if isinstance(value, datetime):
            field_type = "DATE"
        elif isinstance(value, str) and len(value) > 50:
            field_type = "MULTI_LINE_TEXT"
        elif isinstance(value, (list, tuple)):
            field_type = "CHECK_BOX"
        elif isinstance(value, bytearray):
            field_type = "FILE"

        return field_type

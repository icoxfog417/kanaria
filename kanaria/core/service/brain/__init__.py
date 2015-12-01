class Brain(object):
    MY_NAME = "カナリア"
    MY_USER_NAME = "kanaria_administrator"
    TEMPLATE_HEADER = "[kanaria]"

    def __init__(self):
        pass

    @classmethod
    def trim(cls, text):
        t = text.strip().replace("\r", "").replace("\n", "")
        return t

    @classmethod
    def split(cls, text):
        lines = text.split("\n")
        lines = [cls.trim(ln) for ln in lines]
        return lines

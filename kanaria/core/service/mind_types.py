from enum import Enum


class DecisionType(Enum):
    EXECUTE = "EXECUTE"
    HOLD = "HOLD"
    IGNORE = "IGNORE"


class OrderType(Enum):
    CREATE_APPLICATION = "CREATE_APPLICATION"
    ALLOW = "ALLOW"
    ADD_ITEM = "ADD_ITEM"
    MODIFY_ITEM = "MODIFY_ITEM"
    DELETE_ITEM = "DELETE_ITEM"
    POST_LETTER = "POST_LETTER"
    NONE = "NONE"

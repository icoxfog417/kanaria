from pykintone.model import kintoneModel


class Letter(kintoneModel):

    def __init__(self, subject="", body="", from_address="", to_addresses=(), attached_files=()):
        super(Letter, self).__init__()
        self.subject = subject
        self.body = body
        self.from_address = from_address
        self.to_address = self.__to_list(to_addresses)
        self.attached_files = self.__to_list(attached_files)  #todo: have to convert kintone File format

    def from_is(self, name):
        return True if name == self.get_user(self.from_address) else False

    def to_includes(self, name):
        to_users = [self.get_user(a) for a in self.to_address]
        return True if name in to_users else False

    @classmethod
    def __to_list(cls, item):
        if isinstance(item, (list, tuple)):
            if len(item) == 0:
                return []
            else:
                return item
        else:
            return [item]

    @classmethod
    def get_user(cls, address):
        name, domain = address.split("@")
        return name

    @classmethod
    def parse(cls, email):
        # todo: implements email parsing
        return Letter("", "", "", "")

class Letter(object):

    def __init__(self, subject, body, from_address, to_address):
        self.subject = subject
        self.body = body
        self.from_address = from_address
        self.to_address = to_address

    def get_user(self):
        user, domain, _ = self.to_address.split("@")
        return user

    @classmethod
    def parse(cls, email):
        # todo: implements email parsing
        return Letter("", "", "", "")


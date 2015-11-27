class ApplicationIndex(object):

    def __init__(self, app_id, name, address):
        self._id = None
        self.app_id = app_id
        self.name = name
        self.related_uses = []

    @classmethod
    def create(cls, app_id, name):
        # todo: generate address fron name
        address = "kanaria"
        ai = ApplicationIndex(app_id, name, address)
        return ai

class ApplicationIndex(object):

    def __init__(self, app_id, name, code):
        self._id = None
        self.app_id = app_id
        self.name = name
        self.code = code
        self.related_uses = []

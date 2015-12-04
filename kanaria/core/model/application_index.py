class ApplicationIndex(object):

    def __init__(self, app_id, name, code):
        self._id = None
        self.app_id = app_id
        self.name = name
        self.code = code
        self.related_uses = []

    def unique_key(self):
        return self.code

    @classmethod
    def deserialize(cls, application_index_dic):
        aid = application_index_dic
        instance = ApplicationIndex(
            aid["app_id"],
            aid["name"],
            aid["code"]
        )
        instance._id = aid["_id"]
        return instance

from kanaria.core.environment import Environment
from kanaria.core.model import ApplicationIndex


def get_application(name):
    db = Environment.get_db()
    app_index = db.get_collection(ApplicationIndex).find_one({"name": name})
    app_id = app_index["app_id"]

    service = Environment.get_kintone_service()
    app = service.app(app_id)
    return app


def get_members_address():
    # todo: get member's address
    pass

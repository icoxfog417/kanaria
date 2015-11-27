from pykintone.application_settings.administrator import Administrator
import pykintone.application_settings.form_field as ff
from pykintone.application_settings.view import View
from kanaria.core.model import Letter
from kanaria.core.environment import Environment
from kanaria.core.model import ApplicationIndex
from kanaria.core.service.brain import Brain


class Agent(object):

    def __init__(self):
        pass

    def create_application(self, letter, view_name="", as_test_mode=False):
        name = letter.subject
        fields = letter.body.strip().strip("\n")
        fields = [f.replace("\r", "").strip().replace("　", "") for f in fields]

        # validation
        if not name:
            raise Exception("You have to set application name.")
        if len(fields) == 0:
            raise Exception("You have to set at least one field.")

        # create application
        service = Environment.get_kintone_service()
        app_index = None
        with Administrator(service.account) as admin:
            if as_test_mode:
                admin.as_test_mode()

            # create application
            created = admin.create_application(name)

            # create form
            brain = Brain()
            form_fields = []
            for f in fields:
                f_type = brain.get_type_from_text(f)
                f_field = ff.BaseFormField.create(f_type, f, f)
                form_fields.append(f_field)
            admin.form().add(form_fields)

            # create view
            v_name = view_name if view_name else "一覧"
            view = View.create(v_name, fields)
            admin.view().update(view)

            # register application to database
            db = Environment.get_db()
            app_index = ApplicationIndex.create(created.app_id, name)
            db.save(app_index)

        return app_index

    def post(self, letter):
        # todo: implements post letter
        # get application from letter

        # get form information

        # gather form's value and construct dictionary

        # modify application

        # post record

        pass

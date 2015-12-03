# -*- coding: utf-8 -*-
from kanaria.core.model import ApplicationIndex
from kanaria.core.service.brain import Brain


class kintoneInterface(object):

    def __init__(self):
        from kanaria.core.environment import Environment
        self._env = Environment()
        self.service = Environment.get_kintone_service(self._env)
        self.db = Environment.get_db(self._env)

    def get_application_by_code(self, code):
        app_index = self.db.get_collection(ApplicationIndex).find_one({"code": code})
        app = None

        if app_index:
            app_id = app_index["app_id"]
            app = self.service.app(app_id)
        return app

    def get_application_index(self, app_id):
        app_index = self.db.get_collection(ApplicationIndex).find_one({"app_id": app_id})
        return app_index

    def get_member_addresses(self):
        export_api = self.service.user_api().for_exporting
        users = export_api.get_users().users

        addresses = []
        for u in users:
            addresses.append(u.email)
        return addresses

    def get_kanaria(self, create_if_not_exist=False):
        import os
        from pykintone.application_settings.administrator import Administrator
        from pykintone.application_settings.view import View
        import pykintone.application_settings.form_field as ff
        from pykintone.structure_field import File

        app = None
        register = lambda a: self.register_application(a.app_id, Brain.MY_NAME, Brain.MY_USER_NAME)

        # get from database
        app = self.get_application_by_code(Brain.MY_USER_NAME)

        # check existence
        if not app:
            infos = Administrator(self.service.account).select_app_info(name=Brain.MY_NAME).infos
            if len(infos) > 0:
                app = self.service.app(infos[0].app_id)
                register(app)

        if not app and create_if_not_exist:
            app_id = ""
            with Administrator(self.service.account) as admin:
                # create application
                created = admin.create_application(Brain.MY_NAME)
                app_id = created.app_id

                # update general information
                icon = File.upload(os.path.join(os.path.dirname(__file__), "./static/icon.png"))
                admin.general_settings().update({
                    "app": created.app_id,
                    "icon": {
                        "type": "FILE",
                        "file": {
                            "fileKey": icon.file_key
                        }
                    }
                })

                # create form
                fields = [
                    ff.BaseFormField.create("SINGLE_LINE_TEXT", "subject", "Subject"),
                    ff.BaseFormField.create("MULTI_LINE_TEXT", "body", "MessageBody"),
                    ff.BaseFormField.create("SINGLE_LINE_TEXT", "from_address", "From Address"),
                    ff.BaseFormField.create("SINGLE_LINE_TEXT", "to_address", "To Address"),
                    ff.BaseFormField.create("FILE", "attached_files", "Attached Files")
                ]
                admin.form().add(fields)

                # create view
                view = View.create("LetterList", fields)
                admin.view().update(view)

            app = self.service.app(app_id)
            register(app)

        return app

    def create_default_application(self, name, code):
        from pykintone.application_settings.administrator import Administrator
        from pykintone.application_settings.view import View
        import pykintone.application_settings.form_field as ff

        result = None

        with Administrator(self.service.account) as admin:
            # create application
            result = admin.create_application(name)

            # create form
            fields = [
                ff.BaseFormField.create("SINGLE_LINE_TEXT", "subject", "件名"),
                ff.BaseFormField.create("MULTI_LINE_TEXT", "body", "メッセージ"),
                ff.BaseFormField.create("SINGLE_LINE_TEXT", "from_address", "報告者"),
                ff.BaseFormField.create("FILE", "attached_files", "添付ファイル")
            ]
            update_form = admin.form().add(fields, result.app_id)

            # create view
            view = View.create("一覧", ["subject", "from_address"])
            update_view = admin.view().update(view, result.app_id)
            if result.ok and update_form.ok and update_view.ok:
                admin._cached_changes = True
            else:
                raise Exception("Error is occurred when creating default application")

        if result.ok:
            app = self.service.app(result.app_id)
            self.register_application(app.app_id, name, code)
            return app
        else:
            return None

    def copy_application(self, app_id, name, code):
        result = None
        with self.service.administration() as admin:
            result = admin.copy_application(name, app_id)

        if result.ok:
            self.register_application(result.app_id, name, code)
            app = self.service.app(result.app_id)
            return app
        else:
            raise Exception("Error occurred when copying the application")

    def register_application(self, app_id, name, code):
        app_index = ApplicationIndex(app_id, name, code)
        self.db.save(app_index)

    def find_similar_applications(self, name, find_template=False):
        from pykintone.application_settings.administrator import Administrator
        # todo: have to implements more flexible search
        infos = Administrator(self.service.account).select_app_info(name=name).infos

        filtered = []
        for i in infos:
            template = i.name.startswith(Brain.TEMPLATE_HEADER)
            if find_template and template:
                filtered.append(i)
            elif not find_template and not template:
                filtered.append(i)

        return filtered

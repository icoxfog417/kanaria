# -*- coding: utf-8 -*-
from kanaria.core.service.kintone import kintoneInterface
from kanaria.core.service.brain.mind_types import OrderType, DecisionType
from kanaria.core.model.order import Order
from kanaria.core.model.action import Action


def execute(action):
    reply = None
    order_type = action.order.order_type()

    if action.decision_type() == DecisionType.EXECUTE:
        if order_type == OrderType.CREATE_APPLICATION:
            app, app_index = create_application(action)
            if app:
                # first record for new application
                post_order = Order(
                    OrderType.POST_LETTER,
                    action.order.user_address,
                    app.app_id,
                    letter=action.order.letter())
                post(Action(DecisionType.EXECUTE, post_order))
                message = "{0}アプリケーションを作成しました。今後こちらにメールを送っていただければ、アプリケーションにデータが登録されます。".format(app_index.name)
                reply = action.make_reply(message=message, from_user=app_index.code)
            else:
                message = "ごめんなさい、アプリケーションの作成に失敗しちゃいました。。。"
                reply = action.make_reply(message=message)
        elif order_type == OrderType.POST_LETTER:
            created = post(action)
            if not created.ok:
                message = "ごめんなさい、データの登録に失敗しちゃいました。。。このメッセージを担当の人に伝えてください。\n{0}".format(created.error.message)
                reply = action.make_reply(message=message)
        else:
            update_application(action)
    else:
        reply = action.make_reply()

    return reply


def create_application(action, enable_copy=True):
    from kanaria.core.environment import Environment

    kintone = kintoneInterface()
    name = action.order.target
    code = Environment.get_translator(kintone._env).translate(name, "en").replace(" ", "_")
    app_info = kintone.find_similar_applications(name, find_template=True)

    app = None
    app_index = None
    if len(app_info) > 0 and enable_copy:
        app = kintone.copy_application(app_info[0].app_id, name, code)
    else:
        app = kintone.create_default_application(name, code)

    if app:
        app_index = kintone.get_application_index(app.app_id)

    return app, app_index


def update_application(action):
    app_id = action.order.app_id
    field_name = action.order.target
    pass


def post(action):
    from kanaria.core.service.brain.analyzer import TextAnalyzer

    ks = kintoneInterface()
    app = ks.service.app(action.order.app_id)
    letter = action.order.letter()
    analyzer = TextAnalyzer()

    # get form structure
    fields = app.administration().form().get(app.app_id).fields
    data = analyzer.map_letter_to_field(letter, fields)

    # file field
    file_field = [f for f in fields if f.field_type == "FILE"]
    if len(file_field) > 0 and len(letter.attached_files) > 0:
        from pykintone.structure_field import File
        f = File.upload(letter.attached_files[0], app)
        data[file_field[0].code] = {
            "value": {
                "fileKey": f.file_key
            }
        }

    result = app.create(data)
    return result

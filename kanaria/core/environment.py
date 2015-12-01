class Environment(object):

    def __init__(self, config_file=""):
        self.kintone_domain = ""
        self.kintone_id = ""
        self.kintone_password = ""
        self.database_uri = ""
        self.mail_domain = ""
        self.mail_api_key = ""
        self.translator_client_id = ""
        self.translator_client_secret = ""

        import os
        config_file = config_file
        if not config_file:
            default_path = os.path.join(os.path.dirname(__file__), "../../environment.yaml")
            if os.path.isfile(default_path):
                config_file = default_path

        try:
            if config_file:

                with open(config_file) as cf:
                    import yaml
                    e = yaml.load(cf)
                    _get = lambda k, d: "" if not d or k not in d else d[k]
                    yget = lambda k, sk="": _get(k, e) if not sk else _get(sk, _get(k, e))

                    self.kintone_domain = yget("domain")
                    self.kintone_id = yget("login", "id")
                    self.kintone_password = yget("login", "password")
                    self.database_uri = yget("database_uri")
                    self.mail_domain = yget("mail", "domain")
                    self.mail_api_key = yget("mail", "api_key")
                    self.translator_client_id = yget("translator", "client_id")
                    self.translator_client_secret = yget("translator", "client_secret")
            else:
                self.kintone_domain = os.environ.get("KINTONE_DOMAIN", "")
                self.kintone_id = os.environ.get("KINTONE_ID", "")
                self.kintone_password = os.environ.get("KINTONE_PASSWORD", "")
                self.database_uri = os.environ.get("MONGO_URI", "")
                if not self.database_uri:
                    self.database_uri = os.environ.get("MONGOLAB_URI", "")
                if not self.database_uri:
                    self.database_uri = os.environ.get("MONGOHQ_URI", "")
                self.mail_domain = os.environ.get("MAIL_DOMAIN")
                self.mail_api_key = os.environ.get("MAIL_API_KEY")
                self.translator_client_id = os.environ.get("TRANSLATOR_CLIENT_ID")
                self.translator_client_secret = os.environ.get("TRANSLATOR_CLIENT_SECRET")

        except Exception as ex:
            raise Exception("environment is not set. please confirm environment.yaml on your root or environment variables")

    @classmethod
    def get_db(cls):
        from kanaria.core.service.db import MongoDBService
        env = Environment()
        return MongoDBService(env.database_uri)

    @classmethod
    def get_kintone_service(cls):
        from pykintone.account import Account, kintoneService
        env = Environment()
        account = Account(env.kintone_domain, env.kintone_id, env.kintone_password)
        service = kintoneService(account)
        return service

    @classmethod
    def get_translator(cls):
        import pyoxford
        env = Environment()
        translator = pyoxford.translator(env.translator_client_id, env.translator_client_secret)
        return translator

    def make_mail_address(self, user_name):
        return "{0}@{1}".format(user_name, self.mail_domain)

    def __str__(self):
        result = self.kintone_domain + " {0}/{1}".format(self.kintone_id, self.kintone_password)
        result += "\n" + self.database_uri
        return result

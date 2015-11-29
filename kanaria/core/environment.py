class Environment(object):

    def __init__(self, config_file=""):
        self.kintone_domain = ""
        self.kintone_id = ""
        self.kintone_password = ""
        self.database_uri = ""
        self.mail_domain = ""
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
                    self.kintone_domain = e["domain"]
                    self.kintone_id = e["login"]["id"]
                    self.kintone_password = e["login"]["password"]
                    self.database_uri = e["database_uri"]
                    self.mail_domain = e["mail_domain"]
                    self.translator_client_id = e["translator"]["client_id"]
                    self.translator_client_secret = e["translator"]["client_secret"]
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
                self.translator_client_id = os.environ.get("TRANSLATOR_CLIENT_ID")
                self.translator_client_secret = os.environ.get("TRANSLATOR_CLIENT_SECRET")

        except Exception as ex:
            raise Exception("environment is not set. please confirm environment.yaml on your root or environment variables")

        missings = []
        if not self.kintone_domain:
            missings.append("kintone domain")
        if not self.kintone_id:
            missings.append("kintone login id")
        if not self.kintone_password:
            missings.append("kintone login password")
        if not self.database_uri:
            missings.append("database uri")
        if not self.mail_domain:
            missings.append("mail domain")
        if not self.translator_client_id:
            missings.append("translator client_id")
        if not self.translator_client_secret:
            missings.append("translator client_secret")

        if len(missings) > 0:
            raise Exception(", ".join(missings) + " is not set.")

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

    def make_mail_address(self, user_name):
        return "{0}@{1}".format(user_name, self.mail_domain)

    def __str__(self):
        result = self.kintone_domain + " {0}/{1}".format(self.kintone_id, self.kintone_password)
        result += "\n" + self.database_uri
        return result

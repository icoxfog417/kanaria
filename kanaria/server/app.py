import falcon

from email_util import Email
from kanaria.core.agent import Agent


class HelloResource(object):

    def on_post(self, req, resp):
        email = Email()
        letter = email.get_letter(req)
        agent = Agent()
        reply = agent.accept(letter)
        print("subject %s" % reply.subject)
        print("body    %s" % reply.body)
        print(reply.from_address)
        print(reply.to_addresses)
        email.send(subject=reply.subject,
                   text=reply.body,
                   from_address=reply.from_address,
                   to_addresses=reply.to_addresses)


app = falcon.API()
app.add_route("/quote", HelloResource())


if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server("0.0.0.0", 8000, app)
    httpd.serve_forever()
import json
import falcon
import cgi
import io
import os
import pprint
import yaml

import sendgrid

from kanaria.core.model.letter import Letter


class EmailSender(object):

    def __init__(self):
        key_id = self.__get_key_id()
        self.sg = sendgrid.SendGridClient(key_id)
        self.message = sendgrid.Mail()

    def __get_key_id(self):
        base_dir = os.path.dirname(__file__)
        api_key_path = os.path.join(base_dir, 'account.yaml')
        with open(api_key_path) as f:
            account = yaml.load(f)
            return account["api_key"]

    def set_tos(self, *tos):
        self.message.smtpapi.add_to(list(tos))

    def set_from_address(self, from_address):
        self.message.set_from(u'送信者名 <' + from_address + '>')

    def set_subject(self, text):
        self.message.set_subject(text)

    def set_text(self, text):
        self.message.set_text(text)

    def set_html(self, html_text):
        self.message.set_html(html_text)

    def send(self):
        status, msg = self.sg.send(self.message)
        print(status)
        print(msg)


class HelloResource(object):

    def __parse_multipart(self, req):
        ctype, pdict = cgi.parse_header(req.content_type)
        pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')  # convert to byte code for cgi.parse_multipart
        payload = req.stream.read()
        rfile = io.BytesIO(payload)
        if ctype == 'multipart/form-data':
            query = cgi.parse_multipart(rfile, pdict)
            # pprint.pprint(query)
            return query
        else:
            raise Exception("The content-type is unsupported.")

    def __extract_email_info(self, query):
        email_info	= {'subject': '', 'body': '', 'from_address': '', 'to_addresses': [], 'attached_files': []}
        charsets = json.loads(query['charsets'][0].decode('utf-8'))
        envelope = json.loads(query['envelope'][0].decode('utf-8'))
        email_info['from_address'] = envelope['from']
        email_info['to_addresses'] = envelope['to']
        email_info['subject'] = query['subject'][0].decode(charsets['subject'])
        email_info['body'] = query['text'][0].decode(charsets['text'])
        if 'attachment-info' in query:
            attachment_info = json.loads(query['attachment-info'][0].decode("utf-8"))
            for key, val in attachment_info.items():
                content = query[key][0]  # byte string
                attachment = {'filename': val['filename'], 'content': content}
                email_info['attached_files'].append(attachment)

        return email_info

    def send_email(self, subject='', text='', html='', from_address='', to_addresses=()):
        client = EmailSender()
        client.set_tos(gi*to_addresses)
        client.set_from_address(from_address)
        client.set_subject(subject)
        client.set_text(text)
        client.set_html(html)
        client.send()

    def on_post(self, req, resp):
        query = self.__parse_multipart(req)
        email_info = self.__extract_email_info(query)
        letter = Letter(**email_info)
        self.send_email(subject='test', text='neko', from_address=letter.to_address[0], to_addresses=[letter.from_address])

app = falcon.API()
app.add_route("/quote", HelloResource())


if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server("127.0.0.1", 8000, app)
    httpd.serve_forever()
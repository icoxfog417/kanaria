import json
import cgi
import io
import pprint

import sendgrid

from kanaria.core.environment import Environment
from kanaria.core.model.letter import Letter


class Email(object):

    def __init__(self):
        key_id = self.__get_key_id()
        self.sg = sendgrid.SendGridClient(key_id)
        self.message = None

    def __get_key_id(self):
        e = Environment()
        return e.mail_api_key

    def __set_tos(self, tos):
        self.message.smtpapi.add_to(tos)

    def __set_from_address(self, from_address):
        self.message.set_from(u'送信者名 <' + from_address + '>')

    def __set_subject(self, text):
        self.message.set_subject(text)

    def __set_text(self, text):
        self.message.set_text(text)

    def __set_html(self, html_text):
        self.message.set_html(html_text)

    def get_letter(self, req):
        query = self.__parse_multipart(req)
        email_info = self.__extract_email_info(query)
        letter = Letter(**email_info)

        return letter

    def send(self, subject='', text='', html='', from_address='', to_addresses=()):
        self.message = sendgrid.Mail()
        self.__set_tos(to_addresses)
        self.__set_from_address(from_address)
        self.__set_subject(subject)
        self.__set_text(text)
        self.__set_html(html)
        status, msg = self.sg.send(self.message)
        print(status)
        print(msg)

    def __parse_multipart(self, req):
        ctype, pdict = cgi.parse_header(req.content_type)
        pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')  # convert to byte code for cgi.parse_multipart
        payload = req.stream.read()
        rfile = io.BytesIO(payload)
        if ctype == 'multipart/form-data':
            query = cgi.parse_multipart(rfile, pdict)
            pprint.pprint(query)
            return query
        else:
            raise Exception("The content-type is unsupported.")

    def __extract_email_info(self, query):
        email_info = {'subject': '', 'body': '', 'from_address': '', 'to_addresses': [], 'attached_files': []}
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
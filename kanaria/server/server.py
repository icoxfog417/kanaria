import json
import falcon
import cgi
import io
import pprint

from kanaria.core.model.letter import Letter


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

    def on_post(self, req, resp):
        query = self.__parse_multipart(req)
        email_info = self.__extract_email_info(query)
        Letter(email_info)

        quote = {
            'test': 'example',
        }

        resp.body = json.dumps(quote)

app = falcon.API()
app.add_route("/quote", HelloResource())


if __name__ == "__main__":
    from wsgiref import simple_server
    httpd = simple_server.make_server("127.0.0.1", 8000, app)
    httpd.serve_forever()

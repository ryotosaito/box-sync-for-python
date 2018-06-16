# -*- coding: utf-8 -*-

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from urllib import parse

code = ''
domain = '127.0.0.1'
port = 5050
url = 'http://' + domain + ':' + str(port) + '/'

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global code
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        query = parse.parse_qs(parse.urlsplit(self.path).query)
        if 'code' in query:
            code = query['code'][0]
            self.wfile.write(b'Return to your application!')
        else:
            self.wfile.write(b"""
            Something went wrong...<br>
            Your request didn't contain "code" parameter...
            """)

    def log_message(self, format, *args):
        return


def run(server_class=HTTPServer, handler_class=MyHandler):
    server_address = (domain, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.handle_request()
    except KeyboardInterrupt:
        httpd.socket.close()
    return code


if __name__ == '__main__':
    print(run())

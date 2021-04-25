"""
Implementation of a RESTful host that returns Aithre data
"""

import json
import os
import re
import shutil
from http.server import BaseHTTPRequestHandler

from aithre_manager import AithreManager


class AithreHost(BaseHTTPRequestHandler):
    """
    Handles the HTTP response for status.
    """

    HERE = os.path.dirname(os.path.realpath(__file__))
    ROUTES = {
        r'^/aithre': {'GET': AithreManager.get_aithre},
        r'^/illyrians': {'GET': AithreManager.get_illyrians},
        r'^/illyrian': {'GET': AithreManager.get_illyrian}
    }

    def do_HEAD(self):
        self.handle_method('HEAD')

    def do_GET(self):
        self.handle_method('GET')

    def do_POST(self):
        self.handle_method('POST')

    def do_PUT(self):
        self.handle_method('PUT')

    def do_DELETE(self):
        self.handle_method('DELETE')

    def get_payload(self):
        try:
            payload_len = int(self.headers.getheader('content-length', 0))
            payload = self.rfile.read(payload_len)
            payload = json.loads(payload)
            return payload
        except:
            return {}

    def __handle_invalid_route__(self):
        """
        Handles the response to a bad route.
        """
        self.send_response(404)
        self.end_headers()
        self.wfile.write('Route not found\n')

    def __handle_file_request__(self, route, method):
        if method == 'GET':
            try:
                f = open(os.path.join(
                    AithreHost.HERE, route['file']))
                try:
                    self.send_response(200)
                    if 'media_type' in route:
                        self.send_header(
                            'Content-type', route['media_type'])
                    self.end_headers()
                    shutil.copyfileobj(f, self.wfile)
                finally:
                    f.close()
            except:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('File not found\n')
        else:
            self.send_response(405)
            self.end_headers()
            self.wfile.write('Only GET is supported\n')

    def __finish_get_put_delete_request__(self, route, method):
        if method in route:
            content = route[method](self)
            if content is not None:
                self.send_response(200)
                if 'media_type' in route:
                    self.send_header(
                        'Content-type', route['media_type'])
                self.end_headers()
                if method != 'DELETE':
                    self.wfile.write(content.encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('Not found\n')
        else:
            self.send_response(405)
            self.end_headers()
            self.wfile.write(method + ' is not supported\n')

    def __handle_request__(self, route, method):
        if method == 'HEAD':
            self.send_response(200)
            if 'media_type' in route:
                self.send_header('Content-type', route['media_type'])
            self.end_headers()
        else:
            if 'file' in route:
                self.__handle_file_request__(route, method)
            else:
                self.__finish_get_put_delete_request__(route, method)

    def handle_method(self, method):
        route = self.get_route()
        if route is None:
            self.__handle_invalid_route__()
        else:
            self.__handle_request__(route, method)

    def get_route(self):
        for path, route in AithreHost.ROUTES.items():
            if re.match(path, self.path):
                return route
        return None

"""
Module to run a RESTful server to set and get the configuration.
"""

import json
import os
import re
import shutil
from http.server import BaseHTTPRequestHandler, HTTPServer

import aithre

RESTFUL_HOST_PORT = 8081

# EXAMPLES
# Invoke-WebRequest -Uri "http://localhost:8081/aithre" -Method GET -ContentType "application/json"
# Invoke-WebRequest -Uri "http://localhost:8081/illyrian" -Method GET -ContentType "application/json"
# Invoke-WebRequest -Uri "http://localhost:8081/illyrians" -Method GET -ContentType "application/json"
#
# curl -X GET http://localhost:8081/aithre

ERROR_JSON_KEY = 'error'


def get_aithre(
    handler
):
    """
    Creates a response package that gives the current carbon monoxide
    results from an Aithre.
    """
    co_response = {ERROR_JSON_KEY: 'Aithre CO sensor not detected'}

    if aithre.AithreManager.CO_SENSOR is not None:
        co_response = aithre.AithreManager.CO_SENSOR.get_response()
    return json.dumps(
        co_response,
        indent=4,
        sort_keys=False)


def get_all_illrian_response_packages() -> list:
    spo2_levels = []
    serials_reported = []

    for sensor in aithre.AithreManager.SPO2_SENSORS.values():
        serial = sensor.get_serial_number()

        if serial in serials_reported:
            continue

        spo2_levels.append(sensor.get_response())
        serials_reported.append(serial)

    return spo2_levels


def get_illyrians(
    handler
):
    spo2_levels = get_all_illrian_response_packages()

    return json.dumps(
        spo2_levels,
        indent=4,
        sort_keys=False)


def get_illyrian(
    handler
):
    """
    Creates a response package that gives the current blood oxygen levels
    and heartrate from an Illyrian sensor.
    """
    spo2_response = {ERROR_JSON_KEY: 'Illyrian SPO2 sensor not detected'}

    all_responses = get_all_illrian_response_packages()

    if len(all_responses) > 0:
        spo2_response = all_responses[0]

    return json.dumps(
        spo2_response,
        indent=4,
        sort_keys=False)


class AithreHost(BaseHTTPRequestHandler):
    """
    Handles the HTTP response for status.
    """

    HERE = os.path.dirname(os.path.realpath(__file__))
    ROUTES = {
        r'^/aithre': {'GET': get_aithre},
        r'^/illyrians': {'GET': get_illyrians},
        r'^/illyrian': {'GET': get_illyrian}
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


class AithreServer(object):
    """
    Class to handle running a REST endpoint to handle configuration.
    """

    def get_server_ip(
        self
    ):
        """
        Returns the IP address of this REST server.

        Returns:
            string -- The IP address of this server.
        """

        return ''

    def run(
        self
    ):
        """
        Starts the server.
        """

        print("localhost = {}:{}".format(self.__local_ip__, self.__port__))

        self.__http__.serve_forever()

    def stop(
        self
    ):
        if self.__http__ is not None:
            self.__http__.shutdown()
            self.__http__.server_close()

    def __init__(
        self
    ):
        self.__port__ = RESTFUL_HOST_PORT
        self.__local_ip__ = self.get_server_ip()
        server_address = (self.__local_ip__, self.__port__)
        self.__http__ = HTTPServer(server_address, AithreHost)


if __name__ == '__main__':
    host = AithreServer()
    host.run()

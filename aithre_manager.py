"""
Module to run a RESTful server to set and get the configuration.
"""

import json
import os
import re
import shutil
from http.server import BaseHTTPRequestHandler, HTTPServer

from sensors.aithre import Aithre
from sensors.illyrian import Illyrian

RESTFUL_HOST_PORT = 8081

SCAN_PERIOD = 10

# EXAMPLES
# Invoke-WebRequest -Uri "http://localhost:8081/aithre" -Method GET -ContentType "application/json"
# Invoke-WebRequest -Uri "http://localhost:8081/illyrian" -Method GET -ContentType "application/json"
#
# curl -X GET http://localhost:8081/aithre

ERROR_JSON_KEY = 'error'

CO_LEVEL_KEY = "co"
BATTERY_LEVEL_KEY = "battery"

SPO2_LEVEL_KEY = "spo2"
PULSE_KEY = "heartrate"
SIGNAL_STRENGTH_KEY = "signal"


def update_aithre_sensor():
    """
    Attempts to update the Aithre carbon monoxide
    sensor. If the sensor can not be found or is
    not turned on, then the controlling object is
    set to None.
    """
    try:
        if AithreManager.CO_SENSOR is None:
            AithreManager.CO_SENSOR = Aithre()
    except Exception as e:
        print("Attempted to init CO sensor, got e={}".format(e))
        AithreManager.CO_SENSOR = None

    if AithreManager.CO_SENSOR is not None:
        AithreManager.CO_SENSOR.update()


def update_illyrian_sensor():
    """
    Attempts to update the Aithre Illyrian blood oxygen
    sensor. If the sensor can not be found or is
    not turned on, then the controlling object is
    set to None.
    """
    try:
        if AithreManager.SPO2_SENSOR is None:
            AithreManager.SPO2_SENSOR = Illyrian()
    except Exception as e:
        print("Attempted to init SPO2 sensor, got e={}".format(e))
        AithreManager.SPO2_SENSOR = None

    if AithreManager.SPO2_SENSOR is not None:
        AithreManager.SPO2_SENSOR.update()


def get_aithre(
    handler
):
    """
    Creates a response package that gives the current carbon monoxide
    results from an Aithre
    """
    co_response = {ERROR_JSON_KEY: 'Aithre CO sensor not detected'}

    if AithreManager.CO_SENSOR is not None:
        co_response = {
            CO_LEVEL_KEY: AithreManager.CO_SENSOR.get_co_level(),
            BATTERY_LEVEL_KEY: AithreManager.CO_SENSOR.get_battery()}
    return json.dumps(
        co_response,
        indent=4,
        sort_keys=False)


def get_illyrian_v2(
    handler
) -> str:
    """
    Creates a response package that gives the current blood oxygen levels
    and heartrate for ALL Illyrian sensors.

    The V1 endpoint only handled a single sensor.
    """
    if AithreManager.SPO2_SENSOR is not None:
        return [
            {
                SPO2_LEVEL_KEY: AithreManager.SPO2_SENSOR.get_spo2_level(),
                PULSE_KEY: AithreManager.SPO2_SENSOR.get_heartrate(),
                SIGNAL_STRENGTH_KEY: AithreManager.SPO2_SENSOR.get_signal_strength()
            }]

    return json.dumps(
        [],
        indent=4,
        sort_keys=False)


def get_illyrian(
    handler
) -> str:
    """
    Creates a response package that gives the current blood oxygen levels
    and heartrate from an Illyrian sensor.
    """
    spo2_response = {ERROR_JSON_KEY: 'Illyrian SPO2 sensor not detected'}

    if AithreManager.SPO2_SENSOR is not None:
        spo2_response = {
            SPO2_LEVEL_KEY: AithreManager.SPO2_SENSOR.get_spo2_level(),
            PULSE_KEY: AithreManager.SPO2_SENSOR.get_heartrate(),
            SIGNAL_STRENGTH_KEY: AithreManager.SPO2_SENSOR.get_signal_strength()}

    return json.dumps(
        spo2_response,
        indent=4,
        sort_keys=False)


class AithreManager(object):
    """
    Singleton manager class to make sure that the sensor data
    has a common store point.
    """
    CO_SENSOR = None
    SPO2_SENSOR = None

    @staticmethod
    def update_sensors():
        """
        Updates the sensors for all available BlueTooth devices.
        """
        print("Updating Aithre sensors")

        # Global singleton for all to
        # get to the Aithre
        update_aithre_sensor()
        update_illyrian_sensor()


class AithreHost(BaseHTTPRequestHandler):
    """
    Handles the HTTP response for status.
    """

    HERE = os.path.dirname(os.path.realpath(__file__))
    ROUTES = {
        r'^/aithre': {'GET': get_aithre},
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
    ) -> str:
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

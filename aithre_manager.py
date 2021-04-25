"""
Module to run a RESTful server to set and get the configuration.
"""

import json

from aithre_task import AithreTask
from sensors.aithre import Aithre, get_aithre_mac
from sensors.illyrian import Illyrian, get_illyrian_macs

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


class AithreManager(object):
    """
    Singleton manager class to make sure that the sensor data
    has a common store point.
    """
    __CO_SENSOR__ = None
    __SPO2_SENSORS__ = {}

    @staticmethod
    def __update_aithre_sensor__():
        """
        Attempts to update the Aithre carbon monoxide
        sensor. If the sensor can not be found or is
        not turned on, then the controlling object is
        set to None.
        """
        try:
            if AithreManager.__CO_SENSOR__ is None:
                aithre_mac = get_aithre_mac()

                if aithre_mac is not None:
                    AithreManager.__CO_SENSOR__ = Aithre(aithre_mac)
        except Exception as e:
            print("Attempted to init CO sensor, got e={}".format(e))
            AithreManager.__CO_SENSOR__ = None

        if AithreManager.__CO_SENSOR__ is not None:
            AithreManager.__CO_SENSOR__.update()

    @staticmethod
    def __update_illyrian_sensors__():
        """
        Attempts to update the Aithre Illyrian blood oxygen
        sensor. If the sensor can not be found or is
        not turned on, then the controlling object is
        set to None.
        """
        try:
            macs = get_illyrian_macs()

            if macs is not None:
                for illyrian_mac in macs:
                    if illyrian_mac not in AithreManager.__SPO2_SENSORS__:
                        AithreManager.__SPO2_SENSORS__[illyrian_mac] = Illyrian(illyrian_mac)
        except Exception as e:
            print("Attempted to scan and add SPO2 sensors, got e={}".format(e))

        try:
            for illyrian in AithreManager.__SPO2_SENSORS__:
                illyrian.update()
        except Exception as e:
            print("Attempted to update SPO2 sensors, got e={}".format(e))

    @staticmethod
    def update_sensors():
        """
        Updates the sensors for all available BlueTooth devices.
        """
        print("Updating Aithre sensors")

        # Global singleton for all to
        # get to the Aithre
        AithreManager.__update_aithre_sensor__()
        AithreManager.__update_illyrian_sensors__()

    @staticmethod
    def get_aithre(
        handler=None
    ):
        """
        Creates a response package that gives the current carbon monoxide
        results from an Aithre
        """
        co_response = {ERROR_JSON_KEY: 'Aithre CO sensor not detected'}

        if AithreManager.__CO_SENSOR__ is not None:
            co_response = {
                CO_LEVEL_KEY: AithreManager.__CO_SENSOR__.get_co_level(),
                BATTERY_LEVEL_KEY: AithreManager.__CO_SENSOR__.get_battery()}
        return json.dumps(
            co_response,
            indent=4,
            sort_keys=False)

    @staticmethod
    def get_illyrians(
        handler=None
    ) -> str:
        """
        Creates a response package that gives the current blood oxygen levels
        and heartrate for ALL Illyrian sensors.

        The V1 endpoint only handled a single sensor.
        """
        response = []

        for illyrian in AithreManager.__SPO2_SENSORS__:
            try:
                response.append({
                    SPO2_LEVEL_KEY: illyrian.get_spo2_level(),
                    PULSE_KEY: illyrian.get_heartrate(),
                    SIGNAL_STRENGTH_KEY: illyrian.get_signal_strength()
                })
            except:
                response.append({
                    ERROR_JSON_KEY: "Error fetching SPO2"
                })

        return json.dumps(
            response,
            indent=4,
            sort_keys=False)

    @staticmethod
    def get_illyrian(
        handler
    ) -> str:
        """
        Creates a response package that gives the current blood oxygen levels
        and heartrate from an Illyrian sensor.
        """
        spo2_response = {ERROR_JSON_KEY: 'Illyrian SPO2 sensor not detected'}

        if len(AithreManager.__SPO2_SENSORS__) > 0:
            spo2_response = {
                SPO2_LEVEL_KEY: AithreManager.__SPO2_SENSORS__[0].get_spo2_level(),
                PULSE_KEY: AithreManager.__SPO2_SENSORS__[0].get_heartrate(),
                SIGNAL_STRENGTH_KEY: AithreManager.__SPO2_SENSORS__[0].get_signal_strength()}

        return json.dumps(
            spo2_response,
            indent=4,
            sort_keys=False)


__SCAN_PERIOD__ = 10

__UPDATE_TASK__ = AithreTask(
    "UpdateAithre",
    __SCAN_PERIOD__,
    AithreManager.update_sensors,
    None,
    True)

if __name__ == '__main__':
    from aithre_server import AithreServer

    host = AithreServer()
    host.run()

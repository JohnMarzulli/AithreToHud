from logging import Logger
from sys import platform as os_platform

from sensors import bluetooth_device

IS_LINUX = 'linux' in os_platform

if IS_LINUX:
    from bluepy.btle import Scanner

ILLYRIAN_BEACON_SUFFIX = "696C6C70"

SPO2_LEVEL_KEY = "spo2"
PULSE_KEY = "heartrate"
SIGNAL_STRENGTH_KEY = "signal"
SERIAL_KEY = "serial"


def get_value_by_name(
    name_to_find: str
):
    try:
        if not IS_LINUX:
            return None

        scanner = Scanner()
        devices = scanner.scan(2)
        for dev in devices:
            print("    {} {} {}".format(dev.addr, dev.addrType, dev.rssi))

            for (adtype, desc, value) in dev.getScanData():
                try:
                    if name_to_find.lower() in value.lower():
                        return value
                except Exception as ex:
                    print("DevScan loop - ex={}".format(ex))

    except Exception as ex:
        print("Outter loop ex={}".format(ex))

    return None


def get_illyrian(
    mac_adr: str
):
    """
    Attempts to get the blood/pulse/oxygen levels from an Illyrian device
        :param mac_adr: 
    """

    # Example value:
    # '41193dff0008696c6c70'
    # '414039ff0008696c6c70'
    # '410000010008696c6c70'
    #  41[R VALUE * 100][HEART RATE] [SIGNAL STRENGTH][SERIAL NO]696C6C70
    #  [00][0001][0008]
    #  [40][39][ff]
    illyrian = get_value_by_name(ILLYRIAN_BEACON_SUFFIX)

    if illyrian is None:
        return (bluetooth_device.OFFLINE, bluetooth_device.OFFLINE, bluetooth_device.OFFLINE)

    r_value = int(illyrian[2:4], 16) / 100.0
    heartrate = int(illyrian[4:6], 16)
    signal_strength = int(illyrian[6:8], 16)
    serial_number = int(illyrian[8:12], 16)
    sp02 = 109 - (31 * r_value)

    return [[sp02, heartrate, signal_strength], serial_number]


class Illyrian(bluetooth_device.BlueToothDevice):
    def __init__(
        self,
        mac: str,
        logger: Logger = None
    ):
        super(Illyrian, self).__init__(mac, logger=logger)
        self.__serial__ = None
        self.__spo2__ = bluetooth_device.ServiceValue("SPO")
        self.__pulse__ = bluetooth_device.ServiceValue("Pulse")
        self.__signal_strength__ = bluetooth_device.ServiceValue("SignalStrength")

    def __is_connected__(
        self
    ) -> bool:
        return self.__spo2__.is_value_recent() or self.__pulse__.is_value_recent() or self.__signal_strength__.is_value_recent()

    def __update_levels__(
        self
    ):
        """
        Updates the levels of an Illyrian
            :param self: 
        An example value is '410000010008696c6c70' when searching for the MAC.
        This is so the beacon can be used simultaneously by devices.
        """
        try:
            self.log("Attempting Illyrian update")

            new_levels, found_serial = get_illyrian(self.__mac__)

            if found_serial is not None:
                self.__serial__ = found_serial

                self.__spo2__.set_value(new_levels[0])
                self.__pulse__.set_value(new_levels[1])
                self.__signal_strength__.set_value(new_levels[2])
        except:
            self.warn("Unable to get Illyrian levels")

            return None

    def get_serial_number(
        self
    ) -> str:
        return self.__serial__

    def get_spo2_level(
        self
    ):
        """
        Returns the oxygen saturation levels.
            :param self: 
        """

        spo2 = self.__spo2__.get_value()

        return bluetooth_device.OFFLINE if spo2 is None else spo2

    def get_heartrate(
        self
    ):
        """
        Returns the wearer's pulse.
            :param self: 
        """

        pulse = self.__pulse__.get_value()

        return bluetooth_device.OFFLINE if pulse is None else pulse

    def get_signal_strength(
        self
    ):
        """
        Returns the read strength from the sensor.
            :param self: 
        """

        signal = self.__signal_strength__.get_value()

        return bluetooth_device.OFFLINE if signal is None else signal

    def get_response(
        self
    ) -> dict:
        return {
            SPO2_LEVEL_KEY: self.get_spo2_level(),
            PULSE_KEY: self.get_heartrate(),
            SIGNAL_STRENGTH_KEY: self.get_signal_strength(),
            SERIAL_KEY: self.get_serial_number()}

"""
Code and class to interface with Illyrian CO2 blood pulsometers.
"""

from logging import Logger

from sensors.bluetooth_device import OFFLINE, BlueToothDevice
from sensors.device_manager import DeviceManager

ILLYRIAN_BEACON_SUFFIX = "696C6C70"


def get_illyrian_mac():
    """
    Attempts to find the BlueTooth MAC for the
    Aithre Illyrian blood oxygen detector.
    """
    return DeviceManager.INSTANCE.get_mac_by_device_name(ILLYRIAN_BEACON_SUFFIX)


def get_illyrian_macs() -> list:
    """
    Attempts to find any Illyrian devices that are connected.

    Returns an empty list if none are found.
    Returns a list of Macs (in string form) if any are found.

    Returns:
        list: A list of MACs (as strings) of any Illyrians found.
    """

    return DeviceManager.INSTANCE.get_macs_by_device_name(ILLYRIAN_BEACON_SUFFIX)


def get_illyrian(
    mac_adr: str
) -> list:
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
    illyrians = DeviceManager.INSTANCE.get_values_by_name(ILLYRIAN_BEACON_SUFFIX)

    illyrian = illyrians[mac_adr] if mac_adr in illyrians else None

    if illyrian is None:
        return None

    r_value = int(illyrian[2:4], 16) / 100.0
    heartrate = int(illyrian[4:6], 16)
    signal_strength = int(illyrian[6:8], 16)
    serial_number = int(illyrian[8:12], 16)
    sp02 = 109 - (31 * r_value)

    print("sp02:{}, heartrate:{}, signal_strength:{}, serial_number:{}, raw:{}".format(sp02, heartrate, signal_strength, serial_number, illyrian))

    return (sp02, heartrate, signal_strength, serial_number, illyrian)


class Illyrian(BlueToothDevice):
    def __init__(
        self,
        mac: str,
        logger: Logger = None
    ):
        super(Illyrian, self).__init__(mac, logger)

    def _update_levels(
        self
    ):
        """
        Updates the levels of an Illyrian
            :param self: 
        An example value is '410000010008696c6c70' when searching for the MAC.
        This is so the beacon can be used simultaneously by devices.
        """
        try:
            new_levels = get_illyrian(self.__mac__)

            if new_levels is None:
                return False

            self.__levels__ = new_levels

            return True
        except:
            self.warn("Unable to get Illyrian levels")

            return False

    def get_spo2_level(
        self
    ):
        """
        Returns the oxygen saturation levels.
            :param self: 
        """

        if self.__levels__ is not None:
            return self.__levels__[0]

        return OFFLINE

    def get_heartrate(
        self
    ):
        """
        Returns the wearer's pulse.
            :param self: 
        """

        if self.__levels__ is not None:
            return self.__levels__[1]

        return OFFLINE

    def get_signal_strength(
        self
    ):
        """
        Returns the read strength from the sensor.
            :param self: 
        """

        if self.__levels__ is not None:
            return self.__levels__[2]

        return OFFLINE

    def get_serial_number(
        self
    ):
        if self.__levels__ is not None:
            return self.__levels__[3]

        return OFFLINE

    def get_raw_result(
        self
    ):
        if self.__levels__ is not None:
            return self.__levels__[4]

        return OFFLINE

"""
Defines interface for all Aithre bluetooth devices
"""

from datetime import datetime
from logging import Logger
from sys import platform as os_platform

IS_LINUX = 'linux' in os_platform

if IS_LINUX:
    from bluepy.btle import Peripheral

OFFLINE = "OFFLINE"


def get_service_value(
    addr: str,
    addr_type: str,
    offset: str
):
    """
    Gets the value from a Blue Tooth Low Energy device.
    Arguments:
        addr {string} -- The address to get the value from
        add_type {string} -- The type of address we are using.
        offset {string} -- The offset from the device's address to get the value from
    Returns: {int} -- The result of the fetch
    """

    # Generate fake values for debugging
    # and for the development of the visuals.
    if not IS_LINUX:
        return 0

    try:
        p = Peripheral(addr, addr_type)
        ch_all = p.getCharacteristics(uuid=offset)

        if ch_all[0].supportsRead():
            res = ch_all[0].read()

        p.disconnect()

        return ord(res)
    except Exception as ex:
        print("   ex in get_name={}".format(ex))

    return None


class ServiceValue(object):
    EXPECTED_UPDATE_INTERVAL_SECONDS = 120

    def __init__(
        self,
        value_name: str,
        expected_update_interval_seconds: int = 120
    ):
        self.__last_update__ = None
        self.__value_name__ = value_name
        self.__expected_update_interval_seconds__ = expected_update_interval_seconds
        self.__value__ = None

    def __get_value_age__(
        self
    ) -> float:
        if self.__last_update__ is not None:
            return (datetime.utcnow() - self.__last_update__).total_seconds()

        return ServiceValue.EXPECTED_UPDATE_INTERVAL_SECONDS * 1000

    def is_value_recent(
        self
    ) -> bool:
        return self.__get_value_age__() < self.__expected_update_interval_seconds__

    def get_value(
        self
    ) -> any:
        if self.is_value_recent():
            return self.__value__

        return None

    def set_value(
        self,
        value
    ) -> None:
        if value is not None:
            self.__value__ = value
            self.__last_update__ = datetime.utcnow()


class BlueToothDevice(object):
    """
    Base interface class to help define common controls
    and features of the Aithre range of products.
    """

    def log(
        self,
        text: str
    ):
        """
        Logs the given text if a logger is available.

        Arguments:
            text {string} -- The text to log
        """

        if self.__logger__ is not None:
            self.__logger__.log_info_message(text)
        else:
            print("INFO:{}".format(text))

    def warn(
        self,
        text: str
    ):
        """
        Logs the given text if a logger is available AS A WARNING.

        Arguments:
            text {string} -- The text to log
        """

        if self.__logger__ is not None:
            self.__logger__.log_warning_message(text)
        else:
            print("WARN:{}".format(text))

    def __init__(
        self,
        mac: str,
        logger: Logger = None
    ):
        self.__logger__ = logger

        self.warn("Initializing new Aithre object")

        self.__mac__ = mac

    def is_connected(
        self
    ) -> bool:
        """
        Is the BlueTooth device currently connected and usable?

        This is an interface declaration, so each device class will need to
        override this behavior.
        """

        return self.__mac__ is not None and self.__is_connected__()

    def update(
        self
    ):
        """
        Attempts to update the values collected from the device.
        """

        if self.__mac__ is not None:
            self.__update_levels__()

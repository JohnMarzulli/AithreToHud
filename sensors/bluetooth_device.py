"""
Interface definition and common code for interacting with Aithre devices
using Bluetooth
"""

from logging import Logger
from sys import platform as os_platform

try:
    from bluepy.btle import Peripheral, Scanner
except:
    Peripheral = None
    Scanner = None

OFFLINE = "OFFLINE"


def get_service_value(
    addr: str,
    addr_type: str,
    offset: str
) -> int:
    """
    Gets the value from a Blue Tooth Low Energy device.

    Args:
        addr (str): The address to get the value from
        addr_type (str): The type of address we are using.
        offset (str): The offset from the device's address to get the value from

    Returns:
        int: The result of the fetch
    """

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


def get_value_by_name(
    name_to_find: str
) -> str:
    """
    Given a partial device name, attempt to find a device with the value.

    Args:
        name_to_find (str): The partial or complete name of the device.

    Returns:
        str: The value of the first device found, or None if no matches were found.
    """

    try:
        scanner = Scanner()
        devices = scanner.scan()
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


def get_mac_by_device_name(
    name_to_find: str
):
    """
    Attempts to find an Aithre MAC using Blue Tooth low energy.
    Arguments:
        name_to_find {string} -- The name (or partial name) to match the BLE info with.
    Returns: {string} None if a device was not found, otherwise the MAC of the Aithre
    """
    try:
        scanner = Scanner()
        devices = scanner.scan()
        for dev in devices:
            print("    {} {} {}".format(dev.addr, dev.addrType, dev.rssi))

            for (address_type, desc, value) in dev.getScanData():
                try:
                    print("{}:{}:{}".format(address_type, desc, value))
                    if name_to_find.lower() in value.lower():
                        return dev.addr
                except Exception as ex:
                    print("DevScan loop - ex={}".format(ex))

    except Exception as ex:
        print("Outter loop ex={}".format(ex))

    return None


def get_macs_by_device_name(
    name_to_find: str
) -> list:
    """
    Attempts to find an Aithre MAC using Blue Tooth low energy.
    Arguments:
        name_to_find {string} -- The name (or partial name) to match the BLE info with.
    Returns: {string} None if a device was not found, otherwise the MAC of the Aithre
    """
    found_macs = []

    try:
        scanner = Scanner()
        devices = scanner.scan()

        for dev in devices:
            print("    {} {} {}".format(dev.addr, dev.addrType, dev.rssi))

            scan_data = dev.getScanData()

            for (address_type, desc, value) in scan_data:
                try:
                    if name_to_find.lower() in value.lower():
                        found_macs.append(dev.addr)
                except Exception as ex:
                    print("DevScan loop - ex={}".format(ex))
    except Exception as ex:
        print("Outter loop ex={}".format(ex))

    return found_macs


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
        self.__is_linux__ = 'linux' in os_platform

        self.__logger__ = logger

        self.warn("Initializing new Aithre object")

        self.__mac__ = mac
        self._levels_ = None

    def is_connected(
        self
    ):
        """
        Is the BlueTooth device currently connected and usable?
        """

        return (self.__mac__ is not None and self._levels_ is not None)

    def update(
        self
    ):
        """
        Attempts to update the values collected from the device.
        """
        self._update_levels()

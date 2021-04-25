"""
Interface definition and common code for interacting with Aithre devices
using Bluetooth
"""

from logging import Logger
from sys import platform as os_platform

OFFLINE = "OFFLINE"


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

"""
Code to interact with an Aithre carbon monoxide detector.
"""

from logging import Logger

from sensors import bluetooth_device

AITHRE_DEVICE_NAME = "AITHRE"

# The Aithre is always expected to have a public address
AITHRE_ADDR_TYPE = "public"

# Service UUID for the carbon monoxide reading.
# Will be a single character whose ASCII
# value is the parts per million 0 - 255 inclusive
CO_OFFSET = "BCD466FE07034D85A021AE8B771E4922"

# A single character wholes ASCII value is
# the percentage of the battert reminaing.
# The value will be 0 to 100 inclusive.
BAT_OFFSET = "24509DDEFCD711E88EB2F2801F1B9FD1"


def get_aithre_mac():
    """
    Attempts to find the BlueTooth MAC for the
    Aithre Carbon Monoxide detector.
    """
    return bluetooth_device.get_mac_by_device_name(AITHRE_DEVICE_NAME)


def get_aithre(
    mac_adr: str
):
    """
    Gets the current Aithre readings given a MAC for the Aithre
    Arguments:
        mac_adr {string} -- The MAC address of the Aithre to fetch from.
    Returns: {(int, int)} -- The co and battery percentage of the Aithre
    """

    co = bluetooth_device.get_service_value(mac_adr, AITHRE_ADDR_TYPE, CO_OFFSET)
    bat = bluetooth_device.get_service_value(mac_adr, AITHRE_ADDR_TYPE, BAT_OFFSET)

    return co, bat


class Aithre(bluetooth_device.BlueToothDevice):
    def __init__(
        self,
        logger: Logger = None
    ):
        super(Aithre, self).__init__(logger=logger)

    def _update_mac_(
        self
    ):
        """
        Updates the MAC that the Aithre carbon monoxide detector is found at.
        """
        try:
            self._mac_ = get_aithre_mac()
        except Exception as e:
            self._mac_ = None
            self.warn("Got EX={} during MAC update.".format(e))

    def _update_levels(
        self
    ):
        """
        Updates the battery level and carbon monoxide levels that the Aithre CO
        detector has found.
        """
        if self._mac_ is None:
            self.log("Aithre MAC is none while attempting to update levels.")
            if self.__is_linux__:
                self.warn("Aithre MAC is none, attempting to connect.")
                self._update_mac_()

        try:
            self.log("Attempting update")
            new_levels = get_aithre(self._mac_)
            self._levels_ = new_levels
        except Exception as ex:
            # In case the read fails, we will want to
            # attempt to find the MAC of the Aithre again.

            self._mac_ = None
            self.warn(
                "Exception while attempting to update the cached levels.update() E={}".format(ex))

    def get_battery(
        self
    ):
        """
        Gets the battery level of the CO monitor device.
        """
        if self._levels_ is not None:
            return self._levels_[1]

        return bluetooth_device.OFFLINE

    def get_co_level(
        self
    ):
        """
        Gets the current carbon monoxide levels.
        """
        if self._levels_ is not None:
            return self._levels_[0]

        return bluetooth_device.OFFLINE

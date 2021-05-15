from logging import Logger

from sensors import bluetooth_device

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

AITHRE_DEVICE_NAME = "AITHRE"

CO_LEVEL_KEY = "co"
BATTERY_LEVEL_KEY = "battery"


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
        mac: str,
        logger: Logger = None
    ):
        super(Aithre, self).__init__(mac, logger=logger)
        self.__battery__ = bluetooth_device.ServiceValue("Battery")
        self.__co__ = bluetooth_device.ServiceValue("CO")

    def __update_levels__(
        self
    ) -> list:
        """
        Updates the battery level and carbon monoxide levels that the Aithre CO
        detector has found.
        """
        try:
            self.log("Attempting Aithre update")
            new_levels = get_aithre(self.__mac__)

            self.__co__.set_value(new_levels[0])
            self.__battery__.set_value(new_levels[1])
        except Exception as ex:
            # In case the read fails, we will want to
            # attempt to find the MAC of the Aithre again.

            self.warn(
                "Exception while attempting to update the cached levels.update() E={}".format(ex))

            return None

    def get_battery(
        self
    ):
        """
        Gets the battery level of the CO monitor device.
        """
        battery = self.__battery__.get_value()

        return bluetooth_device.OFFLINE if battery is None else battery

    def get_co_level(
        self
    ):
        """
        Gets the current carbon monoxide levels.
        """
        co = self.__co__.get_value()

        return bluetooth_device.OFFLINE if co is None else co

    def get_response(
        self
    ) -> dict:
        return {
            CO_LEVEL_KEY: self.get_co_level(),
            BATTERY_LEVEL_KEY: self.get_battery()}

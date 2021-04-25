import threading

from aithre_task import AithreTask
from bluepy.btle import DefaultDelegate, Peripheral, Scanner

__DEVICE_SCAN_PERIOD__ = 15


class DeviceManager(DefaultDelegate):
    INSTANCE = None

    def __init__(
        self
    ):
        DefaultDelegate.__init__(self)

        self.__devices__ = {}
        self.__peripherals__ = {}
        self.__lock__ = threading.Lock()

        DeviceManager.INSTANCE = self

    def handleDiscovery(
        self,
        dev,
        isNewDev,
        isNewData
    ):
        self.__lock__.acquire()

        print("Callback for {}".format(dev.addr))

        self.__devices__[dev.addr] = dev

        self.__lock__.release()

        if isNewDev:
            print("Discovered device {}".format(dev.addr))
        elif isNewData:
            print("Received new data from {}".format(dev.addr))

    def get_devices(
        self
    ) -> list:
        try:
            self.__lock__.acquire()

            copied_devices = []

            for device in self.__devices__.values():
                copied_devices.append(device)

            return copied_devices
        except Exception as ex:
            print(ex)
            return []
        finally:
            if self.__lock__.locked():
                self.__lock__.release()

    def __get_or_connect_peripheral__(
        self,
        addr: str,
        addr_type: str
    ) -> Peripheral:
        try:
            if addr not in self.__peripherals__:
                new_periph = Peripheral(addr, addr_type)

                self.__peripherals__[addr] = new_periph

            p = self.__peripherals__[addr]

            return p
        except Exception as ex:
            print(ex)
            return None

    def get_service_value(
        self,
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
            p = self.__get_or_connect_peripheral__(addr, addr_type)
            ch_all = p.getCharacteristics(uuid=offset)

            if ch_all[0].supportsRead():
                res = ch_all[0].read()

            return ord(res)
        except Exception as ex:
            print("   ex in get_name={}".format(ex))

        return None

    def get_value_by_name(
        self,
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
            devices = self.get_devices()
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

    def get_values_by_name(
        self,
        name_to_find: str
    ) -> dict:
        """
        Given a partial device name, attempt to find a device with the value.

        Args:
            name_to_find (str): The partial or complete name of the device.

        Returns:
            str: The value of the first device found, or None if no matches were found.
        """

        values = {}

        try:
            devices = self.get_devices()
            for dev in devices:
                print("    {} {} {}".format(dev.addr, dev.addrType, dev.rssi))

                for (adtype, desc, value) in dev.getScanData():
                    try:
                        if name_to_find.lower() in value.lower():
                            values[dev.addr] = value
                    except Exception as ex:
                        print("DevScan loop - ex={}".format(ex))

        except Exception as ex:
            print("Outter loop ex={}".format(ex))

        return values

    def get_mac_by_device_name(
        self,
        name_to_find: str
    ):
        """
        Attempts to find an Aithre MAC using Blue Tooth low energy.
        Arguments:
            name_to_find {string} -- The name (or partial name) to match the BLE info with.
        Returns: {string} None if a device was not found, otherwise the MAC of the Aithre
        """
        try:
            devices = self.get_devices()

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
        self,
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
            devices = self.get_devices()

            for dev in devices:
                print("DEVICE:{} {} {}".format(dev.addr, dev.addrType, dev.rssi))

                scan_data = dev.getScanData()

                for (address_type, desc, value) in scan_data:
                    try:
                        print("    {} {} {}".format(address_type, desc, value))

                        if name_to_find.lower() in value.lower():
                            if "public" not in dev.addrType:
                                pass
                            found_macs.append(dev.addr)
                    except Exception as ex:
                        print("DevScan loop - ex={}".format(ex))
        except Exception as ex:
            print("Outter loop ex={}".format(ex))

        return found_macs


scanner = Scanner().withDelegate(DeviceManager())
scanner.start()

scan_task = AithreTask(
    "ScanDevices",
    __DEVICE_SCAN_PERIOD__,
    scanner.process,
    None,
    True)

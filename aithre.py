import time
from sys import platform as os_platform

from aithre_task import AithreTask
from sensors import aithre, illyrian

IS_LINUX = 'linux' in os_platform

if IS_LINUX:
    from bluepy.btle import Scanner


def get_macs_by_device_name(
    name_to_find: str
):
    """
    Attempts to find an Aithre MAC using Blue Tooth low energy.
    Arguments:
        name_to_find {string} -- The name (or partial name) to match the BLE info with.
    Returns: {string} None if a device was not found, otherwise the MAC of the Aithre
    """
    if not IS_LINUX:
        return []

    macs = []

    try:
        scanner = Scanner()
        devices = scanner.scan(2)
        for dev in devices:
            print("    {} {} {}".format(dev.addr, dev.addrType, dev.rssi))

            for (address_type, desc, value) in dev.getScanData():
                try:
                    if name_to_find.lower() in value.lower():
                        macs.append(dev.addr)
                except Exception as ex:
                    print("DevScan loop - ex={}".format(ex))

    except Exception as ex:
        print("Outter loop ex={}".format(ex))

    return macs


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
        if not IS_LINUX:
            return None

        scanner = Scanner()
        devices = scanner.scan(2)
        for dev in devices:
            print("    {} {} {}".format(dev.addr, dev.addrType, dev.rssi))

            for (address_type, desc, value) in dev.getScanData():
                try:
                    if name_to_find.lower() in value.lower():
                        return dev.addr
                except Exception as ex:
                    print("DevScan loop - ex={}".format(ex))

    except Exception as ex:
        print("Outter loop ex={}".format(ex))

    return None


def get_aithre_mac():
    """
    Attempts to find the BlueTooth MAC for the
    Aithre Carbon Monoxide detector.
    """
    return get_mac_by_device_name(aithre.AITHRE_DEVICE_NAME)


def get_illyrian_macs():
    """
    Attempts to find the BlueTooth MAC for the
    Aithre Illyrian blood oxygen detector.
    """
    return get_macs_by_device_name(illyrian.ILLYRIAN_BEACON_SUFFIX)


SCAN_PERIOD = 10
OFFLINE = "OFFLINE"


def update_aithre_sensor():
    """
    Attempts to update the Aithre carbon monoxide
    sensor. If the sensor can not be found or is
    not turned on, then the controlling object is
    set to None.
    """
    try:
        if AithreManager.CO_SENSOR is None:
            mac = get_aithre_mac()

            if mac is not None and len(mac) > 0:
                AithreManager.CO_SENSOR = aithre.Aithre(mac)
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
    illyrian_macs = get_illyrian_macs()

    for mac in illyrian_macs:
        if mac not in AithreManager.SPO2_SENSORS:
            AithreManager.SPO2_SENSORS[mac] = illyrian.Illyrian(mac)

        AithreManager.SPO2_SENSORS[mac].update()


class AithreManager(object):
    """
    Singleton manager class to make sure that the sensor data
    has a common store point.
    """
    CO_SENSOR = None
    SPO2_SENSORS = {}

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


update_task = AithreTask(
    "UpdateAithre",
    SCAN_PERIOD,
    AithreManager.update_sensors,
    None,
    True)

if __name__ == '__main__':
    while True:
        try:
            if AithreManager.CO_SENSOR is not None:
                print("CO:{}PPM BAT:{}%".format(
                    AithreManager.CO_SENSOR.get_co_level(),
                    AithreManager.CO_SENSOR.get_battery()))

            if AithreManager.SPO2_SENSOR is not None:
                print("SPO2:{}%, {}BPM, SIGNAL:{}".format(
                    AithreManager.SPO2_SENSOR.get_spo2_level(),
                    AithreManager.SPO2_SENSOR.get_heartrate(),
                    AithreManager.SPO2_SENSOR.get_signal_strength()))
        except:
            print("Exception in debug loop")

        time.sleep(SCAN_PERIOD)

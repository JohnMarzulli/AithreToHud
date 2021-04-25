import time

from sensors.device_manager import DeviceManager

while True:
    devices = DeviceManager.INSTANCE.get_devices()

    for dev in devices:
        print("{} {} {}".format(dev.addr, dev.addrType, dev.rssi))

        for (address_type, desc, value) in dev.getScanData():
            print("    {}:{}:{}".format(address_type, desc, value))
    
    time.sleep(15)

"""
Console application to help debug Aithre bluetooth device connectivity.
"""

import time

import aithre_manager
from aithre_task import AithreTask

update_task = AithreTask(
    "UpdateAithre",
    aithre_manager.SCAN_PERIOD,
    aithre_manager.AithreManager.update_sensors,
    None,
    True)

if __name__ == '__main__':
    while True:
        try:
            if aithre_manager.AithreManager.CO_SENSOR is not None:
                print("CO:{}PPM BAT:{}%".format(
                    aithre_manager.AithreManager.CO_SENSOR.get_co_level(),
                    aithre_manager.AithreManager.CO_SENSOR.get_battery()))

            if aithre_manager.AithreManager.SPO2_SENSOR is not None:
                print("SPO2:{}%, {}BPM, SIGNAL:{}".format(
                    aithre_manager.AithreManager.SPO2_SENSOR.get_spo2_level(),
                    aithre_manager.AithreManager.SPO2_SENSOR.get_heartrate(),
                    aithre_manager.AithreManager.SPO2_SENSOR.get_signal_strength()))
        except:
            print("Exception in debug loop")

        time.sleep(aithre_manager.SCAN_PERIOD)

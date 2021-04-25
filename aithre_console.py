"""
Console application to help debug Aithre bluetooth device connectivity.
"""

import time

import aithre_manager

if __name__ == '__main__':
    while True:
        print("Aithre:{}".format(aithre_manager.AithreManager.get_aithre()))
        print("Illyrians:{}".format(aithre_manager.AithreManager.get_illyrians()))

        time.sleep(10)

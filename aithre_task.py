"""
Module to handle tasks that occur on a regularly scheduled interval.
"""

import datetime
import sys
import threading
import time
from logging import Logger


class AithreTask(object):
    """
    Object to control and handle a recurring task.
    """

    def start(
        self
    ):
        """
        Starts the task if it is not already running.
        """
        if self.__task_callback__ is not None \
            and self.__thread__ is not None \
                and not self.__thread__.isAlive():
            self.__is_running__ = True
            self.__thread__.start()

            return True

        return False

    def __run_loop__(
        self
    ):
        while True:
            task_start_time = datetime.datetime.utcnow()
            try:
                self.__task_callback__()
            except Exception as e:
                # + sys.exc_info()[0]
                error_mesage = "EX({}):{}".format(self.__task_name__, e)

                if self.__logger__ is not None:
                    self.__logger__.info(error_mesage)
                else:
                    print(error_mesage)
            task_run_time = datetime.datetime.utcnow() - task_start_time
            time_to_sleep = self.__task_interval__ - task_run_time.total_seconds()

            if time_to_sleep > 0.0:
                print("{}: Sleeping for {} seconds".format(
                    self.__task_name__,
                    time_to_sleep))
                time.sleep(time_to_sleep)

    def __init__(
        self,
        task_name: str,
        task_interval: float,
        task_callback,
        logger: Logger = None,
        start_immediate: bool = True
    ):
        """
        Creates a new reccurring task.
        The call back is called at the given time schedule.
        """

        self.__task_name__ = task_name
        self.__task_interval__ = task_interval
        self.__task_callback__ = task_callback
        self.__logger__ = logger
        self.__thread__ = threading.Thread(
            target=self.__run_loop__
        )

        if start_immediate:
            self.start()

"""
Implementation of a HOST service that returns Aithre data.
"""

from http.server import HTTPServer

from aithre_host import AithreHost

RESTFUL_HOST_PORT = 8081


class AithreServer(object):
    """
    Class to handle running a REST endpoint to handle configuration.
    """

    def get_server_ip(
        self
    ) -> str:
        """
        Returns the IP address of this REST server.

        Returns:
            string -- The IP address of this server.
        """

        return ''

    def run(
        self
    ):
        """
        Starts the server.
        """

        print("localhost = {}:{}".format(self.__local_ip__, self.__port__))

        self.__http__.serve_forever()

    def stop(
        self
    ):
        if self.__http__ is not None:
            self.__http__.shutdown()
            self.__http__.server_close()

    def __init__(
        self
    ):
        self.__port__ = RESTFUL_HOST_PORT
        self.__local_ip__ = self.get_server_ip()
        server_address = (self.__local_ip__, self.__port__)
        self.__http__ = HTTPServer(server_address, AithreHost)


if __name__ == '__main__':
    host = AithreServer()
    host.run()

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

from config import OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT


class OscTransmitter():
    def __init__(self, receive_ip: str, receive_port: int, send_ip: str,
                 send_port: int):
        self._receive_ip = receive_ip
        self._receive_port = receive_port
        self._send_ip = send_ip
        self._send_port = send_port

        self._dispatcher = Dispatcher()
        self._udp_client = udp_client.SimpleUDPClient(self._send_ip,
                                                      self._send_port)

    def map(self, address: str, func):
        ''' Create a OSC message mapping based on `func`, and send it to `address`
        Args:
        - address: an address where the function receives messages
        - func: a function: (address, message, client)
        '''
        def callback(addr, message):
            func(addr, message, self._udp_client)

        self._dispatcher.map(address, callback)

    def serve(self):
        self._server = osc_server.ThreadingOSCUDPServer(
            (self._receive_ip, self._receive_port), self._dispatcher)
        print("Serving on {}".format(self._server.server_address))
        self._server.serve_forever()


class OscSender():
    def __init__(self, send_ip, send_port, root_address=''):
        self._send_ip = send_ip
        self._send_port = send_port
        self._root_address = root_address

        self._udp_client = udp_client.SimpleUDPClient(self._send_ip,
                                                      self._send_port)

    def send(self, address, message):
        self._udp_client.send_message(self._root_address + address, message)


if __name__ == '__main__':

    def send_to_sclang(addr, message, client):
        print(message)
        client.send_message(addr, message)

    osc_trans = OscTransmitter(OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT)
    osc_trans.map("/vsynth/vco/1", send_to_sclang)
    osc_trans.map("/vsynth/vco/2", send_to_sclang)
    osc_trans.serve()

from config import OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

from param_mapper import ParamMapper

client = udp_client.SimpleUDPClient(SC_IP, SC_PORT)


def send_to_sclang(addr, message):
    print(message)
    client.send_message(addr, message)


dispatcher = Dispatcher()
dispatcher.map("/vsynth/vco/1", send_to_sclang)
dispatcher.map("/vsynth/vco/2", send_to_sclang)
server = osc_server.ThreadingOSCUDPServer((OSC_BRIDGE_IP, OSC_BRIDGE_PORT),
                                          dispatcher)

print("Serving on {}".format(server.server_address))
server.serve_forever()

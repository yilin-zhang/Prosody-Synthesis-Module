from osc_handlers import OscTransmitter
from config import OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT


def transmit_to_sclang(addr, message, client):
    print(message)
    client.send_message(addr, message)


if __name__ == '__main__':
    osc_trans = OscTransmitter(OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT)
    osc_trans.map("/vsynth/vco/1", transmit_to_sclang)
    osc_trans.map("/vsynth/vco/2", transmit_to_sclang)
    osc_trans.serve()

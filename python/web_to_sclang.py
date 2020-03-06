from osc_handlers import OscTransmitter
from config import OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT


def transmit_to_sclang(addr, message, osc_sender):
    print(message)
    osc_sender.send(addr, message)


if __name__ == '__main__':
    osc_trans = OscTransmitter(OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT,
                               '/web', '/vsynth')
    osc_trans.map("/vco/1", transmit_to_sclang)
    osc_trans.map("/vco/2", transmit_to_sclang)
    osc_trans.map("/note/velocity", transmit_to_sclang)
    osc_trans.map("/note/note_on", transmit_to_sclang)
    osc_trans.map("/note/note_off", transmit_to_sclang)
    osc_trans.serve()

from osc_handlers import OscTransmitter
from config import OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT

from param_mapper import ParamMapper

def transmit_to_sclang(addr, message, osc_sender):
    print(message)
    osc_sender.send(addr, message)

def get_handlers(mapper):
    osc_addr = {
        'vowel1_f1': '/formant/vowel1/f1',
        'vowel1_f2': '/formant/vowel1/f2',
        'vowel2_f1': '/formant/vowel2/f1',
        'vowel2_f2': '/formant/vowel2/f2',
        'lf_ratio': '/feature/lf_ratio',
        'hf_ratio': '/feature/hf_ratio',
        'detune': '/feature/detune',
        'attack': '/feature/attack',
        'tune': '/feature/tune',
        'vibrato': '/feature/vibrato',
        'brightness': '/feature/brightness',
        'noisiness': '/feature/noisiness',
    }

    def param_handler(addr, message, osc_sender):
        param = addr.split('/')[-1]
        output_dict = mapper.send_event(param, float(message))
        for output_param, val in output_dict.items():
            osc_sender.send(osc_addr[output_param], val)

    def velocity_handler(addr, message, osc_sender):
        osc_sender.send(addr, message)

    def note_on_handler(addr, message, osc_sender):
        param_handler(addr, message, osc_sender)
        osc_sender.send(addr, message)

    def note_off_handler(addr, message, osc_sender):
        osc_sender.send(addr, message)

    return param_handler, velocity_handler, note_on_handler, note_off_handler

if __name__ == '__main__':
    mapper = ParamMapper()
    param_handler, velocity_handler, note_on_handler, note_off_handler = get_handlers(mapper)

    osc_trans = OscTransmitter(OSC_BRIDGE_IP, OSC_BRIDGE_PORT, SC_IP, SC_PORT,
                               '/gui', '/vsynth')

    osc_trans.map("/note/velocity", velocity_handler)
    osc_trans.map("/note/note_on", note_on_handler)
    osc_trans.map("/note/note_off", note_off_handler)

    osc_trans.map("/feature/tune", param_handler)
    osc_trans.map("/feature/vibrato", param_handler)
    osc_trans.map("/feature/brightness", param_handler)
    osc_trans.map("/feature/noisiness", param_handler)

    osc_trans.map("/emotion/valence", param_handler)
    osc_trans.map("/emotion/power", param_handler)

    osc_trans.serve()

import mido
import os
import sys
from watchgod import watch

from param_mapper import ParamMapper
from osc_handlers import MidiOscConverter
from config import SC_IP, SC_PORT, MIDI_DEVICE


def get_handlers(param_mapper):
    osc_addr = {
        'vowel1_f1': '/formant/vowel1/f1',
        'vowel1_f2': '/formant/vowel1/f2',
        'vowel2_f1': '/formant/vowel2/f1',
        'vowel2_f2': '/formant/vowel2/f2',
        'attack': '/feature/attack',
        'tune': '/feature/tune',
        'vibrato': '/feature/vibrato',
        'brightness': '/feature/brightness',
        'noisiness': '/feature/noisiness',
    }

    def note_on_handler(note, velocity, osc_sender):
        output_dict = param_mapper.send_event('note_on')
        for output_param, val in output_dict.items():
            osc_sender.send(osc_addr[output_param], val)
        osc_sender.send('/note/velocity', velocity / 127)
        osc_sender.send('/note/note_on', note)

    def note_off_handler(note, osc_sender):
        osc_sender.send('/note/note_off', note)

    def cc_handler(control_num, control_val, osc_sender):
        output_dict = {}
        if control_num == 1:
            output_dict = param_mapper.send_event(
                'valence', (control_val / 127. - 0.5) * 2)
        elif control_num == 2:
            output_dict = param_mapper.send_event(
                'power', (control_val / 127. - 0.5) * 2)
        elif control_num == 3:
            output_dict = param_mapper.send_event('tune',
                                                  (control_val - 64) / 64.)
        elif control_num == 4:
            output_dict = param_mapper.send_event('vibrato',
                                                  (control_val / 127.))
        elif control_num == 5:
            output_dict = param_mapper.send_event('brightness',
                                                  (control_val / 127.))
        elif control_num == 6:
            output_dict = param_mapper.send_event('noisiness',
                                                  (control_val / 127.))

        for output_param, val in output_dict.items():
            osc_sender.send(osc_addr[output_param], val)

    return note_on_handler, note_off_handler, cc_handler


def watch_dir(dir_path, midi_osc_converter):
    ''' Watches a directory, and send midi messages whenever a new MIDI file
    is created in it.
    Arg:
    - dir_path: path to the direcory to be watched
    '''
    for changes in watch(dir_path):
        for change in changes:
            status, path = change
            # omit the `.DS_Store`
            if os.path.basename(path) == '.DS_Store':
                continue
            if status.name == 'added' and path.endswith('.mid'):
                print('new midi message')
                # sock.sendto(bytes('h', 'utf-8'), ('192.168.1.5', 4210))
                mid = mido.MidiFile(path)
                for msg in mid:
                    midi_osc_converter.send_osc(msg)


def realtime_input(midi_osc_converter):
    with mido.open_input(MIDI_DEVICE) as inport:
        while True:
            msg = inport.receive()
            midi_osc_converter.send_osc(msg)


if __name__ == '__main__':
    param_mapper = ParamMapper()
    note_on_handler, note_off_handler, cc_handler = get_handlers(param_mapper)
    midi_osc_converter = MidiOscConverter(SC_IP, SC_PORT, note_on_handler,
                                          note_off_handler, cc_handler)
    if len(sys.argv) < 2:
        realtime_input(midi_osc_converter)
    else:
        dir_path = sys.argv[1]
        watch_dir(dir_path, midi_osc_converter)

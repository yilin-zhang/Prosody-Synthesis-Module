import mido
import os
import sys
from watchgod import watch

from param_mapper import ParamMapper
from osc_handlers import MidiOscConverter
from config import SC_IP, SC_PORT


def get_handlers(param_mapper):
    osc_addr = {
        'vowel1_f1': '/formant/vowel1/f1',
        'vowel1_f2': '/formant/vowel1/f2',
        'vowel2_f1': '/formant/vowel2/f1',
        'vowel2_f2': '/formant/vowel2/f2',
        'tune': '/feature/tune',
        'vibrato': '/feature/vibrato',
        'brightness': '/feature/brightness',
        'noiseness': '/feature/noiseness',
    }

    def note_on_handler(note, velocity, osc_sender):
        output_dict = param_mapper.map_formants()
        for output_param, val in output_dict.items():
            osc_sender.send(osc_addr[output_param], val)
        osc_sender.send('/note/velocity', velocity)
        osc_sender.send('/note/note_on', note)

    def note_off_handler(note, osc_sender):
        osc_sender.send('/note/note_off', note)

    def cc_handler(control_num, control_val, osc_sender):
        output_dict = {}
        if control_num in (0, 1):
            if control_num == 0:
                output_dict = param_mapper.update_and_map(
                    'valence', (control_val / 127. - 0.5) * 2)
            elif control_num == 1:
                output_dict = param_mapper.update_and_map(
                    'power', (control_val / 127. - 0.5) * 2)
        elif control_num == 2:
            output_dict = param_mapper.update_and_map('tune',
                                                      (control_val - 64) / 64.)
        elif control_num == 3:
            output_dict = param_mapper.update_and_map('vibrato',
                                                      (control_val / 127.))
        elif control_num == 4:
            output_dict = param_mapper.update_and_map('brightness',
                                                      (control_val / 127.))
        elif control_num == 5:
            output_dict = param_mapper.update_and_map('noiseness',
                                                      (control_val / 127.))

        for output_param, val in output_dict.items():
            osc_sender.send(osc_addr[output_param], val)

    return note_on_handler, note_off_handler, cc_handler


def send_osc_msg(midi_path, midi_osc_converter):
    ''' Sends midi messages in a midi file.
    Arg:
    - midi_path: path to a midi file.
    '''
    mid = mido.MidiFile(midi_path)
    for msg in mid:
        midi_osc_converter.send_osc(msg)


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
            elif status.name == 'added' and path.endswith('.mid'):
                print('new midi message')
                # sock.sendto(bytes('h', 'utf-8'), ('192.168.1.5', 4210))
                send_osc_msg(path, midi_osc_converter)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('You should specify a directory.\n')
        sys.exit(-1)
    else:
        dir_path = sys.argv[1]

    param_mapper = ParamMapper()
    note_on_handler, note_off_handler, cc_handler = get_handlers(param_mapper)
    midi_osc_converter = MidiOscConverter(SC_IP, SC_PORT, note_on_handler,
                                          note_off_handler, cc_handler)
    watch_dir(dir_path, midi_osc_converter)

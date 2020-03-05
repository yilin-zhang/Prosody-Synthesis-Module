import mido
import time
import os
import sys
from watchgod import watch

from osc_handle import OscSender
from param_mapper import ParamMapper


class MidiOscConverter():
    def __init__(self, send_ip, send_port, root_address='/vsynth'):
        self._osc_sender = OscSender(send_ip, send_port, root_address)
        self._param_mapper = ParamMapper()

    def send_osc(self, midi_message):
        if midi_message.type == 'note_on':
            self._osc_sender.send('/note/velocity', midi_message.velocity)
            self._osc_sender.send('/note/note_on', midi_message.note)
        elif midi_message.type == 'note_off':
            self._osc_sender.send('/note/note_off', midi_message.note)
        # TODO: maybe move this out of this class
        elif (midi_message.type == 'control_change'):
            control_num = midi_message.control
            control_val = midi_message.value
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
            output_dict = {}
            if control_num in (0, 1):
                if control_num == 0:
                    output_dict = self._param_mapper.update_param(
                        'valence', (control_val / 127. - 1) * 2)
                elif control_num == 1:
                    output_dict = self._param_mapper.update_param(
                        'power', (control_val / 127. - 1) * 2)
            elif control_num == 2:
                output_dict = self._param_mapper.update_param(
                    'tune', (control_val / 127. - 1) * 2)
            elif control_num == 3:
                output_dict = self._param_mapper.update_param(
                    'vibrato', (control_val / 127))
            elif control_num == 4:
                output_dict = self._param_mapper.update_param(
                    'brightness', (control_val / 127))
            elif control_num == 5:
                output_dict = self._param_mapper.update_param(
                    'noiseness', (control_val / 127))

            for output_param, val in output_dict.items():
                self._osc_sender.send(osc_addr[output_param], val)

        time.sleep(midi_message.time)
        print('valence:', self._param_mapper.get_param('valence'))
        print('power:', self._param_mapper.get_param('power'))


if __name__ == '__main__':
    midi_osc_converter = MidiOscConverter('127.0.0.1', 57121)

    def send_midi_msg(midi_path: str):
        ''' Sends midi messages in a midi file.
        Arg:
        - midi_path: path to a midi file.
        '''
        port = mido.open_output()
        mid = mido.MidiFile(midi_path)
        for msg in mid:
            # time.sleep(msg.time)
            # new_msgs = []
            midi_osc_converter.send_osc(msg)

    def watch_dir(dir_path: str):
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
                    send_midi_msg(path)

    if len(sys.argv) < 2:
        sys.stderr.write('You should specify a directory.\n')
        sys.exit(-1)
    else:
        dir_path = sys.argv[1]

    watch_dir(dir_path)

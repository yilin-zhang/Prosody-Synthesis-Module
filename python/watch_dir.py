# external libs
import sys
import os
import time
import socket
from watchgod import watch
import mido

# internal lib
from cc_mapper import CCMapper


def send_midi_msg(midi_path: str, cc_mapper: CCMapper):
    ''' Sends midi messages in a midi file.
    Arg:
    - midi_path: path to a midi file.
    '''
    port = mido.open_output()
    mid = mido.MidiFile(midi_path)
    for msg in mid:
        time.sleep(msg.time)
        new_msgs = []
        if (msg.type == 'control_change'):
            new_msgs = cc_mapper.map(msg)
        else:
            new_msgs.append(msg)

        for m in new_msgs:
            if not m.is_meta:
                port.send(m)


def watch_dir(dir_path: str, cc_mapper: CCMapper):
    ''' Watches a directory, and send midi messages whenever a new MIDI file
    is created in it.
    Arg:
    - dir_path: path to the direcory to be watched
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for changes in watch(dir_path):
        for change in changes:
            status, path = change
            # omit the `.DS_Store`
            if os.path.basename(path) == '.DS_Store':
                continue
            elif status.name == 'added' and path.endswith('.mid'):
                print('new midi message')
                sock.sendto(bytes('h', 'utf-8'), ('192.168.1.8', 4210))
                send_midi_msg(path, cc_mapper)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('You should specify a directory.\n')
        sys.exit(-1)
    else:
        dir_path = sys.argv[1]

    cc_mapper = CCMapper()

    watch_dir(dir_path, cc_mapper)

from watchgod import watch
import mido
import sys
import os
import time


def send_midi_msg(midi_path):
    port = mido.open_output()
    mid = mido.MidiFile(midi_path)
    for msg in mid:
        time.sleep(msg.time)
        if not msg.is_meta:
            port.send(msg)


def watch_dir(dir_path):
    for changes in watch(dir_path):
        for change in changes:
            status, path = change
            # omit the `.DS_Store`
            if os.path.basename(path) == '.DS_Store':
                continue
            elif status.name == 'added' and path.endswith('.mid'):
                print('new midi message')
                send_midi_msg(path)


if len(sys.argv) < 2:
    sys.stderr.write('You should specify a directory.\n')
    exit(-1)
else:
    dir_path = sys.argv[1]

watch_dir(dir_path)

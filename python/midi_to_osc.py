import mido
import time
import os
import sys
from watchgod import watch

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import udp_client


client = udp_client.SimpleUDPClient("127.0.0.1", 57120)

def send_to_sclang(to_addr, message):
    client.send_message(to_addr, message)


def send_midi_msg(midi_path: str):
    ''' Sends midi messages in a midi file.
    Arg:
    - midi_path: path to a midi file.
    '''
    port = mido.open_output()
    mid = mido.MidiFile(midi_path)
    for msg in mid:
        time.sleep(msg.time)
        # new_msgs = []
        if (msg.type == 'control_change'):
            continue
        else:
            if msg.type == 'note_on':
                send_to_sclang('/vsynth/note/velocity', msg.velocity)
                send_to_sclang('/vsynth/note/note_on', msg.note)
            elif msg.type == 'note_off':
                send_to_sclang('/vsynth/note/note_off', msg.note)



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

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('You should specify a directory.\n')
        sys.exit(-1)
    else:
        dir_path = sys.argv[1]


    watch_dir(dir_path)
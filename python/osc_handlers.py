import time
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import udp_client


class OscSender():
    def __init__(self, send_ip, send_port, root_address=''):
        self._send_ip = send_ip
        self._send_port = send_port
        self._root_address = root_address

        self._udp_client = udp_client.SimpleUDPClient(self._send_ip,
                                                      self._send_port)

    def send(self, address, message):
        self._udp_client.send_message(self._root_address + address, message)


class OscTransmitter():
    def __init__(self,
                 receive_ip: str,
                 receive_port: int,
                 send_ip: str,
                 send_port: int,
                 receive_root='',
                 send_root=''):
        self._receive_ip = receive_ip
        self._receive_port = receive_port
        self._send_ip = send_ip
        self._send_port = send_port
        self._receive_root = receive_root
        self._send_root = send_root

        self._dispatcher = Dispatcher()
        self._osc_sender = OscSender(self._send_ip, self._send_port,
                                     self._send_root)

    def map(self, address: str, func):
        ''' Create a OSC message mapping based on `func`, and send it to `address`
        Args:
        - address: an address where the function receives messages
        - func: a function: (address, message, client)
        '''
        def callback(addr, message):
            addr = '/' + '/'.join(addr.split('/')[2:])  # remove the root
            func(addr, message, self._osc_sender)

        self._dispatcher.map(self._receive_root + address, callback)

    def serve(self):
        self._server = osc_server.ThreadingOSCUDPServer(
            (self._receive_ip, self._receive_port), self._dispatcher)
        print("Serving on {}".format(self._server.server_address))
        self._server.serve_forever()


class MidiOscConverter():
    def __init__(self,
                 send_ip,
                 send_port,
                 note_on_handler=False,
                 note_off_handler=False,
                 cc_handler=False,
                 root_address='/vsynth'):
        self._osc_sender = OscSender(send_ip, send_port, root_address)
        self._note_on_handler = note_on_handler
        self._note_off_handler = note_off_handler
        self._cc_handler = cc_handler

    def send_osc(self, midi_message):
        time.sleep(midi_message.time)
        if midi_message.type == 'note_off' or (midi_message.type == 'note_on' and
                                               midi_message.velocity == 0):
            note = midi_message.note
            self._note_off_handler(note, self._osc_sender)
        elif midi_message.type == 'note_on':
            note = midi_message.note
            velocity = midi_message.velocity
            self._note_on_handler(note, velocity, self._osc_sender)
        elif (self._cc_handler and midi_message.type == 'control_change'):
            control_num = midi_message.control
            control_val = midi_message.value
            self._cc_handler(control_num, control_val, self._osc_sender)

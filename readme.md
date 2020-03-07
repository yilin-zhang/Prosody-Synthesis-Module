# Prosody Synthesis Module

This project provides:
1. A SuperCollider `.scd` file that comes with a vocal `SynthDef` and OSC
   receiving functionality.
3. A web control panel (work in progress)
2. Two Python OSC modules that handle OSC transmit and MIDI-to-OSC respectively.
3. A Python prosody feature mapping module.

Workflow
```
Web Interface / MIDI -> (OSC) -> Feature Mapping and OSC Transmit -> (OSC) -> SuperCollider
```

## Set-up

### Prerequisite
Make sure you have Python, SuperCollider, Node.js and `npm` installed.

In `python/` directory, run the following command to install Python dependencies:
``` shell
pip install -r requirements.txt
```

In `js/` directory, run the following command to install Node.js dependencies:
``` shell
npm i
```

Most of the time, you need a configuration file to make it work properly. To do
this, put a file `config.yml` in the project root. Here's a configuration
example:

``` yaml
osc_bridge_ip: 127.0.0.1
osc_bridge_port: 8088
sc_ip: 127.0.0.1
sc_port: 57120

midi_device: MPKmini2
```

Usually you only need to change the `sc_port` and `midi_device` entries.

To check all the available devices on your computer, go to your Python REPL,
type in the following commands:

``` python
>>> import mido
>>> mido.get_output_names()
```

### SuperCollider

Run `sclang/vsynth_osc.scd` on SuperCollider. Most of the time you need to run
`NetAddr.langPort` to know the current OSC port in use. Make sure this port is
the same as you specified in the `sc_port` entry in `config.yml`.

### Web Interface

Run `npm start` to start the web interface.

Also run `python/web_to_sclang` to enable the OSC transmit.

### MIDI Input

Make sure you have installed all the required packages. Run
`python/midi_to_sclang` to enable MIDI input. If there's no more argument, the
program reads only MIDI messages from the hardware. You can also give it a file
path, such as `../midi`, where the program will watch the file change and send
the MIDI messages in the newly-created MIDI file.

Some CC numbers are used to send control parameters:
- CC1 Valence
- CC2 Power
- CC3 Tune (microtone control, +- 100 cents, value 64 -> 0 cent)
- CC4 Vibrato
- CC5 Brightness
- CC6 Noisiness

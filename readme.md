# Shimi Prosody Synthesis Module

## MIDI File Watching

`watch_dir.py`

Watch directory for sending midi data. package `watchgod` is required.

Usage:

``` python
python watch_dir.py path/to/dir
```

## Sound Synthesis

`vsynth.scd`

Vocal synthesis module. Use SuperCollider to set up (run all the code).

Control Parameter:
- CC0 Valence
- CC1 Power
- CC2 Tune (microtone control, +- 100 cents, value 64 -> 0 cent)
- CC3 Vibrato
- CC4 Brightness
- CC5 Noisiness

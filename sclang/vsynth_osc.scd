s.boot;

///////////////////////////////////////////////////////////
// Define the vocal synth

SynthDef(\vsynth, {
	arg freq=440, amp=0.1, osc1_amp=0, osc2_amp=0,
	tune=0, vibrato=0, brightness=1, noisiness=0,
	detune=0, lf_ratio=1, hf_ratio=1, attack=0, vowel1_f1=0, vowel1_f2=0, vowel2_f1=0, vowel2_f2=0,
	gate=0, out=0;

	var detune_freq, vibrato_lfo, src, noise_src, sig_f1, sig_f2, sig_h, sig_l, sig;
	var vibrato_noise = LFNoise1.kr(10);
	var noise_env, env;
	var vowel_trans = Rand.new(0.1, 0.2);

	// sound source settings
	freq = Lag.kr(freq, 0.1);
	vibrato = Lag.kr(vibrato, 0.1);

	// vibrato
	vibrato_lfo = ((freq.cpsmidi+tune)+(vibrato*SinOsc.kr(6+(1.0*vibrato_noise),0,0.5))).midicps;
	detune_freq = (vibrato_lfo.cpsmidi+detune).midicps;
	src = (Saw.ar(vibrato_lfo, mul: osc1_amp) + Saw.ar(detune_freq, mul: osc2_amp));

	// add noise
	noise_src = LPF.ar(PinkNoise.ar(0.05) * noisiness, brightness*1000+500, 10);

	// source signal
	sig = noise_src + src;

	// HF-LF control
	sig_l = LPF.ar(sig, 3000, rq: 1.0, mul: lf_ratio);
	sig_h = HPF.ar(sig, 3000, rq: 1.0, mul: hf_ratio);
	sig = sig_l + sig_h;

	// LPF (brightness control)
	sig = LPF.ar(sig, (brightness*10000)+5000);

	// formant settings
	sig_f1 = BPF.ar(sig, XLine.kr(vowel1_f1, vowel2_f1, attack+vowel_trans), 0.8, 0.9);
	sig_f1 = BPF.ar(sig_f1, XLine.kr(vowel1_f1, vowel2_f1, attack+vowel_trans), 0.1, 0.9);
	//sig_f1 = BPF.ar(sig_f1, XLine.kr(vowel1_f1, vowel2_f1, attack+vowel_trans), 0.1, 1.2);

	sig_f2 = BPF.ar(sig, XLine.kr(vowel1_f2, vowel2_f2, attack+vowel_trans), 0.5, 1.3);
	sig_f2 = BPF.ar(sig_f2, XLine.kr(vowel1_f2, vowel2_f2, attack+vowel_trans), 0.3, 1.3);
	sig_f2 = BPF.ar(sig_f2, XLine.kr(vowel1_f2, vowel2_f2, attack+vowel_trans), 0.15, 1.3);

	sig = sig_f1 + sig_f2;

	env = EnvGen.kr(
		Env.adsr(attack, 0.05, 0.8, Rand.new(0.1, 0.3)),
		gate,
		doneAction:2
	);

	sig = env * sig * amp * 3;

	Out.ar(out, Limiter.ar(sig.dup, 0.95));

}).add;


///////////////////////////////////////////////////////////
// Define global variables

// Notes
~notes = Array.fill(128, {nil});
//~notes.postcs;
~velocity = 0;

// Oscillators
~osc1_val = 0.7;
~osc2_val = 0.3;

// Parameters
// Emotion-driven parameters
~vowel1_f1_val = 0;
~vowel1_f2_val = 0;
~vowel2_f1_val = 0;
~vowel2_f2_val = 0;
~attack_val = 0;
~lf_ratio_val = 1;
~hf_ratio_val = 1;
~detune_val = 0;
// Directly controlled parameters
~tune_val = 0;
~vibrato_val = 0.3;
~brightness_val = 1;
~noisiness_val = 0;


///////////////////////////////////////////////////////////
// Osc Receiving

OSCdef.new(\note_velocity, {
	arg msg, time, addr, port;
	~velocity = msg[1].asFloat;
}, '/vsynth/note/velocity');

OSCdef.new(\note_on, {
	arg msg, time, addr, port;
	var val = msg[1].asInt;
	val.postln;
	~notes[val].set(\gate, 0);
	~notes[val] = Synth.new(\vsynth, [
		\freq, val.midicps,
		\amp, ~velocity.linexp(0.0, 1.0, 0.05, 1), // volume control
		\gate, 1,
		\out, 0,
		\detune, ~detune_val,
		\attack, ~attack_val,
		\lf_ratio, ~lf_ratio_val,
		\hf_ratio, ~hf_ratio_val,
		\tune, ~tune_val,
		\vibrato, ~vibrato_val,
		\noisiness, ~noisiness_val,
		\brightness, ~brightness_val,
		\osc1_amp, ~osc1_val,
		\osc2_amp, ~osc2_val,
		\vowel1_f1, ~vowel1_f1_val,
		\vowel1_f2, ~vowel1_f2_val,
		\vowel2_f1, ~vowel2_f1_val,
		\vowel2_f2, ~vowel2_f2_val,
	]);
}, '/vsynth/note/note_on');

OSCdef.new(\note_off, {
	arg msg, time, addr, port;
	var val = msg[1].asInt;
	~notes[val].set(\gate, 0);
	~notes[val] = nil;
}, '/vsynth/note/note_off');

// VCO

OSCdef.new(\vco_1, {
	arg msg, time, addr, port;
	var val = msg[1].asFloat;
	~osc1_val = val;
	~notes.do {|note| note.set(\osc1_amp, ~osc1_val)};
}, '/vsynth/vco/1');

OSCdef.new(\vco_2, {
	arg msg, time, addr, port;
	var val = msg[1].asFloat;
	~osc2_val = val;
	~notes.do {|note| note.set(\osc2_amp, ~osc2_val)};
}, '/vsynth/vco/2');

// Emotion driven parameters

OSCdef.new(\v1_f1, {
	arg msg, time, addr, port;
	~vowel1_f1_val = msg[1].asFloat;
}, '/vsynth/formant/vowel1/f1');

OSCdef.new(\v1_f2, {
	arg msg, time, addr, port;
	~vowel1_f2_val = msg[1].asFloat;
}, '/vsynth/formant/vowel1/f2');

OSCdef.new(\v2_f1, {
	arg msg, time, addr, port;
	~vowel2_f1_val = msg[1].asFloat;
}, '/vsynth/formant/vowel2/f1');

OSCdef.new(\v2_f2, {
	arg msg, time, addr, port;
	~vowel2_f2_val = msg[1].asFloat;
}, '/vsynth/formant/vowel2/f2');

OSCdef.new(\attack, {
	arg msg, time, addr, port;
	~attack_val = msg[1].asFloat;
}, '/vsynth/feature/attack');

OSCdef.new(\lf_ratio, {
	arg msg, time, addr, port;
	~lf_ratio_val = msg[1].asFloat;
}, '/vsynth/feature/lf_ratio');

OSCdef.new(\hf_ratio, {
	arg msg, time, addr, port;
	~hf_ratio_val = msg[1].asFloat;
}, '/vsynth/feature/hf_ratio');

OSCdef.new(\detune, {
	arg msg, time, addr, port;
	~detune_val = msg[1].asFloat;
}, '/vsynth/feature/detune');

// Directly controlled parameters

OSCdef.new(\tune, {
	arg msg, time, addr, port;
	~tune_val = msg[1].asFloat;
	~notes.do{|note| note.set(\tune, ~tune_val)};
}, '/vsynth/feature/tune');

OSCdef.new(\vibrato, {
	arg msg, time, addr, port;
	~vibrato_val = msg[1].asFloat;
	~notes.do{|note| note.set(\vibrato, ~vibrato_val)};
}, '/vsynth/feature/vibrato');

OSCdef.new(\noisiness, {
	arg msg, time, addr, port;
	~noisiness_val = msg[1].asFloat;
	~notes.do{|note| note.set(\noisiness, ~noisiness_val)};
}, '/vsynth/feature/noisiness');

OSCdef.new(\brightness, {
	arg msg, time, addr, port;
	~brightness_val = msg[1].asFloat;
	~notes.do{|note| note.set(\brightness, ~brightness_val)};
}, '/vsynth/feature/brightness');

"Listening on: ".post;
NetAddr.langPort.postln;

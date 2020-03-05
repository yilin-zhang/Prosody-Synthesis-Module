///////////////////////////////////////////////////////////
// Define the vocal synth - vsynth

// | Vowel | F1 (Hz) | F2 (Hz) |
// |-------+---------+---------|
// | a     |     756 |    1391 |
// | i     |     277 |    2321 |
// | u     |     300 |    1863 |

(
SynthDef(\vsynth,{
	arg freq=440, amp=0.1, osc1_amp=0, osc2_amp=0,
	tune=0.5, vib=0, brightness=1, noise=0,
	vowel1_f1=0, vowel1_f2=0, vowel2_f1=0, vowel2_f2=0,
	gate=0, out=0;

	var noiseSrc, output;
	var vibrato, src;
	var vibratonoise = LFNoise1.kr(10);
	var cutoff1, cutoff2;
	var env;
	var vowel_trans = Rand.new(0.1, 0.5);

	// sound source settings
	freq = Lag.kr(freq, 0.1);
	vib = Lag.kr(vib, 0.1);
	// vibrato = ((freq.cpsmidi)+(Line.kr(0.0,vib,2.5)*SinOsc.kr(6+(1.0*vibratonoise),0,0.5))).midicps;
	vibrato = ((freq.cpsmidi+((tune-0.5)*2))+(vib*SinOsc.kr(6+(1.0*vibratonoise),0,0.5))).midicps;
	src = Pulse.ar(vibrato, mul: osc1_amp*0.5) + Saw.ar(vibrato, mul: osc2_amp*0.5);

	// formant settings
	src = BPF.ar(src, XLine.kr(vowel1_f1, vowel2_f1, vowel_trans), 0.2, 2);
	src = BPF.ar(src, XLine.kr(vowel1_f2, vowel2_f2, vowel_trans), 0.5, 4);

	// add noise
	noiseSrc = WhiteNoise.ar(0.03);
	output= LPF.ar(src+(noise*noiseSrc), (brightness*6000)+1000);

	env = EnvGen.kr(
		Env.adsr(Rand.new(0.01, 0.1), 0.1, 0.8, Rand.new(0.1, 0.3)),
		gate,
		doneAction:2
	);

	output = env * output;

	Out.ar(out,output.dup)

}).add;
)

///////////////////////////////////////////////////////////
// Define global variables
(
~notes = Array.fill(128, {nil});
~notes.postcs;
~velocity = 0;

// GUI
//~slider_size = [30, 150];
//~slider_y = 50; // the y-axis position
//~knob_size = 30;
//~txt_y = 30;

~formants = [
	[675, 1550], // a (650~700), (1510~1590)
	[350, 2120], // i (310~390), (1970~2170)
	[390, 1390]  // u (350~430), (1380~1410)
];

~control_ranges = [
	[75, 150],
	[120, 150],
	[90, 70]
];

// Oscillators
~osc1_val = 0.8;
~osc2_val = 0.8;

// CC
~vowel1_val = 0;                     // CC0
~vowel1_f1_val = ~formants[0][0];    // CC1
~vowel1_f2_val = ~formants[0][1];    // CC2
~vowel2_val = 1;                     // CC3
~vowel2_f1_val = ~formants[1][0];    // CC4
~vowel2_f2_val = ~formants[1][1];    // CC5
~tune_val = 0;                       // CC6
~vib_val = 0;                        // CC7
~brightness_val = 0;                 // CC8
~noise_val = 0;                      // CC9


)

///////////////////////////////////////////////////////////
// Osc Example
(
OSCdef.new(\note_on, {
	arg msg, time, addr, port;
	var val = msg[1].asInt;

	~notes[val] = Synth.new(\vsynth, [
		\freq, val.midicps,
		\amp, ~velocity.linexp(1, 127, 0.05, 1), // volume control
		\gate, 1,
		\out, 0,
		\vib, ~vib_val,
		\noise, ~noise_val,
		\brightness, ~brightness_val,
		\osc1_amp, ~osc1_val,
		\osc2_amp, ~osc2_val,
		\vowel1_f1, ~vowel1_f1_val,
		\vowel1_f2, ~vowel1_f2_val,
		\vowel2_f1, ~vowel2_f1_val,
		\vowel2_f2, ~vowel2_f2_val,
	]);
}, '/vsynth/note/note_on');

OSCdef.new(\vco_1, {
	arg msg, time, addr, port;
	var val = msg[1].asFloat;
	~osc1_val = val;
	~notes.do {|note| note.set(\osc1_amp, ~osc1_val)};
}, 'vsynth/vco/1');

OSCdef.new(\vco_2, {
	arg msg, time, addr, port;
	var val = msg[1].asFloat;
	~osc2_val = val;
	~notes.do {|note| note.set(\osc2_amp, ~osc2_val)};
}, 'vsynth/vco/2');

OSCdef.new(\note_off, {
	arg msg, time, addr, port;
	var val = msg[1].asInt;
	~notes[val].set(\gate, 0);
	~notes[val] = nil;
}, '/vsynth/note/note_off');

OSCdef.new(\note_velocity, {
	arg msg, time, addr, port;
	~velocity = msg[1].asInt;
}, '/vsynth/note/velocity');
)
NetAddr.langPort;
"1".asInt + 1;

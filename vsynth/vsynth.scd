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
// MIDI controls
(
MIDIIn.connectAll; // connect all MIDI devices to SC (will run .init automatically)

MIDIFunc.trace(false); // print all the MIDI information

MIDIdef.noteOn(\on, {
	arg val, num, chan, src;
	// calculate the formants based on valence&power

	//{~sl2d_fm.valueAction_(~fm_val)}.defer;
	~vowel1_f1_val.postln;
	~vowel1_f2_val.postln;
	~vowel2_f1_val.postln;
	~vowel2_f2_val.postln;
	~notes[num] = Synth.new(\vsynth, [
		\freq, num.midicps,
		\amp, val.linexp(1, 127, 0.05, 1), // volume control
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
});

MIDIdef.noteOff(\off, {
	arg val, num, chan, src;
	[val, num, chan, src].postln;
	~notes[num].set(\gate, 0);
	~notes[num] = nil; // remove the synth from the array, since the synth has been freed
});

MIDIdef.cc(\cc_vowel1, {
	arg val, num, chan;
	~vowel1_val = val;
	//{~sl2d_fm.activex_(val/127)}.defer;
}, 0);

MIDIdef.cc(\cc_vowel1_f1, {
	arg val, num, chan;
	~vowel1_f1_val = switch(~vowel1_val,
		{0}, {~control_ranges[0][0] * (val / 127 - 0.5) * 2 + ~formants[0][0]},
		{1}, {~control_ranges[1][0] * (val / 127 - 0.5) * 2 + ~formants[1][0]},
		{2}, {~control_ranges[2][0] * (val / 127 - 0.5) * 2 + ~formants[2][0]},
	);
	//{~sl2d_fm.activex_(val/127)}.defer;
}, 1);

MIDIdef.cc(\cc_vowel1_f2, {
	arg val, num, chan;
	~vowel1_f2_val = switch(~vowel1_val,
		{0}, {~control_ranges[0][1] * (val / 127 - 0.5) * 2 + ~formants[0][1]},
		{1}, {~control_ranges[1][1] * (val / 127 - 0.5) * 2 + ~formants[1][1]},
		{2}, {~control_ranges[2][1] * (val / 127 - 0.5) * 2 + ~formants[2][1]},
	);
	//{~sl2d_fm.activex_(val/127)}.defer;
}, 2);

MIDIdef.cc(\cc_vowel2, {
	arg val, num, chan;
	~vowel2_val = val;

	//{~sl2d_fm.activex_(val/127)}.defer;
}, 3);

MIDIdef.cc(\cc_vowel2_f1, {
	arg val, num, chan;
	~vowel2_f1_val = switch(~vowel2_val,
		{0}, {~control_ranges[0][0] * (val / 127 - 0.5) * 2 + ~formants[0][0]},
		{1}, {~control_ranges[1][0] * (val / 127 - 0.5) * 2 + ~formants[1][0]},
		{2}, {~control_ranges[2][0] * (val / 127 - 0.5) * 2 + ~formants[2][0]},
	);
	//{~sl2d_fm.activex_(val/127)}.defer;
}, 4);

MIDIdef.cc(\cc_vowel2_f2, {
	arg val, num, chan;
	~vowel2_f2_val = switch(~vowel2_val,
		{0}, {~control_ranges[0][1] * (val / 127 - 0.5) * 2 + ~formants[0][1]},
		{1}, {~control_ranges[1][1] * (val / 127 - 0.5) * 2 + ~formants[1][1]},
		{2}, {~control_ranges[2][1] * (val / 127 - 0.5) * 2 + ~formants[2][1]},
	);
	//{~sl2d_fm.activex_(val/127)}.defer;
}, 5);

MIDIdef.cc(\cc_tune, {
	arg val, num, chan;
	~tune_val = val/127;
	~notes.do{|note| note.set(\tune, ~tune_val)};
	//{~kb_tune.valueAction_(val/128)}.defer; // 64 -> no tune
}, 6);

MIDIdef.cc(\cc_vib, {
	arg val, num, chan;
	~vib_val = val/127;
	~notes.do{|note| note.set(\vib, ~vib_val)};
	//{~kb_vib.valueAction_(val/127)}.defer;
}, 7);

MIDIdef.cc(\cc_brightness, {
	arg val, num, chan;
	~brightness_val = val/127;
	~notes.do{|note| note.set(\brightness, ~brightness_val)};
	//{~kb_brightness.valueAction_(val/127)}.defer;
}, 8);

MIDIdef.cc(\cc_noise, {
	arg val, num, chan;
	~noise_val = val/127;
	~notes.do{|note| note.set(\noise, ~noise_val)};
	//{~kb_noise.valueAction_(val/127)}.defer;
}, 9);


)

///////////////////////////////////////////////////////////
// Osc Example
(
OSCdef.new(
	\toggle,
	{
		arg msg, time, addr, port;
		[msg, time, addr, port].postln;
	},
	'/frompython'
)
)
NetAddr.langPort;

///////////////////////////////////////////////////////////
// Build GUI elements
/*
(
// w.close;
w = Window.new("VSynth", Rect(500, 200, 350, 400));
w.front;


// OSC1 volume slider
~sl_osc1 = Slider.new(w, Rect(50, ~slider_y, ~slider_size[0], ~slider_size[1]))
.action_({
	arg sl;
	~notes.do{|note| note.set(\osc1_amp, sl.value); ~osc1_val=sl.value;};
});
~txt_osc1 = StaticText(w, Rect(45, ~txt_y, 200, 20))
.string = "Pulse";

// OSC2 volume slider
~sl_osc2 = Slider.new(w, Rect(90, ~slider_y, ~slider_size[0], ~slider_size[1]))
.action_({
	arg sl;
	~notes.do{|note| note.set(\osc1_amp, sl.value); ~osc2_val=sl.value;};
});
~txt_osc2 = StaticText(w, Rect(85, ~txt_y, 200, 20))
.string = "Saw";

// frequency slider
~kb_tune = Knob.new(w, Rect(130, ~slider_y, ~knob_size, ~knob_size))
.mode_(\vert)
.value_(0.5)
.action_({
	arg sl;
	~notes.do{|note| note.set(\tune, sl.value); ~tune_val=sl.value;};
});
~txt_tune = StaticText(w, Rect(170, ~slider_y, 200, 20))
.string = "Tune";

// vibrato slider
~kb_vib = Knob.new(w, Rect(130, ~slider_y+40, ~knob_size, ~knob_size))
.action_({
	arg sl;
	~notes.do{|note| note.set(\vib, sl.value); ~vib_val=sl.value;};
	//~vsynth.set(\vib, sl.value);
})
.mode_(\vert);
~txt_vib = StaticText(w, Rect(170, ~slider_y+40, 200, 20))
.string = "Vibrato";

// brightness slider
~kb_brightness = Knob.new(w, Rect(130, ~slider_y+80, ~knob_size, ~knob_size))
.action_({
	arg sl;
	~notes.do{|note| note.set(\brightness, sl.value); ~brightness_val=sl.value;};
	//~vsynth.set(\brightness, sl.value);
})
.mode_(\vert);
~txt_brightness = StaticText(w, Rect(170, ~slider_y+80, 200, 20))
.string = "Brightness";

// noisiness slider
~kb_noise = Knob.new(w, Rect(130, ~slider_y+120, ~knob_size, ~knob_size))
.action_({
	arg sl;
	~notes.do{|note| note.set(\noise, sl.value); ~noise_val=sl.value;};
	//~vsynth.set(\noise, sl.value);
})
.mode_(\vert);
~txt_noise = StaticText(w, Rect(170, ~slider_y+120, 200, 20))
.string = "Noisiness";


// Formant control
~sl2d_fm = Slider2D.new(w, Rect(30, 220, 100, 100))
.action_({
	arg sl;
	var x = (sl.x - 0.5) *2; // valence
	var y = (sl.y - 0.5) *2; // power
	~valence = x;     // -1.0~+1.0
	~power = y;       // -1.0~+1.0
});

)
*/

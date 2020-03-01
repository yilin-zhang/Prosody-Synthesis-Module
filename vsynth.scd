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

~slider_size = [30, 150];
~slider_y = 50; // the y-axis position
~knob_size = 30;
~txt_y = 30;

~osc1_val = 0;
~osc2_val = 0;
~tune_val = 0;
~vib_val = 0;
~brightness_val = 0;
~noise_val = 0;

~valence = 0;
~power = 0;

~formants = [
	[675, 1550], // a (650~700), (1510~1590)
	[350, 2120], // i (310~390), (1970~2170)
	[390, 1390]  // u (350~430), (1380~1410)
];

~control_ranges = [
//	[25, 40],
//	[40, 50],
//	[40, 30]
	[75, 150],
	[120, 150],
	[90, 70]
];
)
///////////////////////////////////////////////////////////
// MIDI controls
(
MIDIIn.connectAll; // connect all MIDI devices to SC (will run .init automatically)

MIDIFunc.trace(true); // print all the MIDI information

MIDIdef.noteOn(\on, {
	arg val, num, chan, src;
	// calculate the formants based on valence&power
	var vowel1 = [0, 1, 2].choose;
	var range1 = ~control_ranges[vowel1];
	var vowel1_f1 = ~formants[vowel1][0];
	var vowel1_f2 = ~formants[vowel1][1];

	var vowel2 = [0, 1, 2].choose;
	var range2 = ~control_ranges[vowel2];
	var vowel2_f1 = ~formants[vowel2][0];
	var vowel2_f2 = ~formants[vowel2][1];

	if (vowel1 == 0) { // a
		vowel1_f1 = vowel1_f1 + (range1[0] * ((0.3*~valence) + (0.7*~power)));
		vowel1_f2 = vowel1_f2 + (range1[1] * ((0.9*~valence) + (0.1*~power)));
	};
	if (vowel1 == 1) { // i
		vowel1_f1 = vowel1_f1 + (range1[0] * ((-0.3*~valence) + (0.7*~power)));
		vowel1_f2 = vowel1_f2 + (range1[1] * ((0.7*~valence) + (0.3*~power)));
	};
	if (vowel1 == 2) { // u
		vowel1_f1 = vowel1_f1 + (range1[0] * ((0.4*~valence) + (-0.6*~power)));
		vowel1_f2 = vowel1_f2 + (range1[1] * ((0.3*~valence) + (-0.7*~power)));
	};

	if (vowel2 == 0) { // a
		vowel2_f1 = vowel2_f1 + (range2[0] * ((0.3*~valence) + (0.7*~power)));
		vowel2_f2 = vowel2_f2 + (range2[1] * ((0.9*~valence) + (0.1*~power)));
	};
	if (vowel2 == 1) { // i
		vowel2_f1 = vowel2_f1 + (range2[0] * ((-0.3*~valence) + (0.7*~power)));
		vowel2_f2 = vowel2_f2 + (range2[1] * ((0.7*~valence) + (0.3*~power)));
	};
	if (vowel2 == 2) { // u
		vowel2_f1 = vowel2_f1 + (range2[0] * ((0.4*~valence) + (0.6*~power)));
		vowel1_f2 = vowel2_f2 + (range2[1] * ((0.3*~valence) + (-0.7*~power)));
	};

	//{~sl2d_fm.valueAction_(~fm_val)}.defer;
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
		\vowel1_f1, vowel1_f1,
		\vowel1_f2, vowel1_f2,
		\vowel2_f1, vowel2_f1,
		\vowel2_f2, vowel2_f2,
	]);
});

MIDIdef.noteOff(\off, {
	arg val, num, chan, src;
	[val, num, chan, src].postln;
	~notes[num].set(\gate, 0);
	~notes[num] = nil; // remove the synth from the array, since the synth has been freed
});

MIDIdef.cc(\cc_valence, {
	arg val, num, chan;
	{~sl2d_fm.activex_(val/127)}.defer;
}, 0);

MIDIdef.cc(\cc_power, {
	arg val, num, chan;
	{~sl2d_fm.activey_(val/127)}.defer;
}, 1);

MIDIdef.cc(\cc_tune, {
	arg val, num, chan;
	{~kb_tune.valueAction_(val/128)}.defer; // 64 -> no tune
}, 2);

MIDIdef.cc(\cc_vib, {
	arg val, num, chan;
	{~kb_vib.valueAction_(val/127)}.defer;
}, 3);

MIDIdef.cc(\cc_brightness, {
	arg val, num, chan;
	{~kb_brightness.valueAction_(val/127)}.defer;
}, 4);

MIDIdef.cc(\cc_noise, {
	arg val, num, chan;
	{~kb_noise.valueAction_(val/127)}.defer;
}, 5);


)

///////////////////////////////////////////////////////////
// Build GUI elements
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

// Color palette: https://www.color-hex.com/color-palette/91866

var emotionPanel, paramKnobs, keyButtons, volumeSlider;
var mainLayout, upperLayout;
var panelLayout, knobsLayout, knobLayouts, keyboardLayout, volumeLayout;
var panelText, vcoText, knobTexts, volumeText;
var oscAddr;

var velocity=1.0;

Window.closeAll;
w = Window.new("VSynth", Rect(500, 200, 380, 250))
.background_(Color.fromHexString("#e9dbd5"));
oscAddr = NetAddr.new("127.0.0.1", 8088);

///////////////////////////////////////////////////////////////////
// Emotion Panel
emotionPanel = Slider2D.new()
.background_(Color.fromHexString("#c0a5a1"))
.x_(0.5).y_(0.5)
.action_({|panel|
	oscAddr.sendMsg("/web/emotion/valence", panel.x.linlin(0.0, 1.0, -1.0, 1.0));
	oscAddr.sendMsg("/web/emotion/power", panel.y.linlin(0.0, 1.0, -1.0, 1.0));
});
panelText = StaticText.new().string_("Valence × Power");
panelLayout = VLayout.new([panelText, align: \center], emotionPanel);

///////////////////////////////////////////////////////////////////
// Volume Slider
volumeSlider = Slider.new()
.background_(Color.fromHexString("#a68886")).value_(1.0);
volumeText = StaticText.new().string_("Velocity");
volumeLayout = VLayout.new([volumeText, align: \center], volumeSlider);

///////////////////////////////////////////////////////////////////
// Parameter Knobs
paramKnobs = 4.collect {
	Knob.new()
	.mode_(\vert)
	.background_(Color.fromHexString("#876a64"));
};
paramKnobs[0]
.value_(0.5)               // Tune in the middle
.action_({|knob|
	oscAddr.sendMsg("/web/feature/tune", knob.value.linlin(0.0, 1.0, -1.0, 1.0));
});
paramKnobs[1]
.value_(0.3)  // Vibrato 0.3
.action_({|knob|
	oscAddr.sendMsg("/web/feature/vibrato", knob.value);
});
paramKnobs[2]
.value_(1)    // Brightness 1.0
.action_({|knob|
	oscAddr.sendMsg("/web/feature/brightness", knob.value);
});
paramKnobs[3]
.action_({|knob|
	oscAddr.sendMsg("/web/feature/noisiness", knob.value);
});
knobTexts = Array.new(4);
knobTexts.add(StaticText.new().string_("Tune"));
knobTexts.add(StaticText.new().string_("Vibrato"));
knobTexts.add(StaticText.new().string_("Brightness"));
knobTexts.add(StaticText.new().string_("Noisiness"));
knobLayouts = 4.collect { |i|
	HLayout.new(
		paramKnobs[i],
		knobTexts[i]
	)
};
knobsLayout = VLayout.new(*knobLayouts);

///////////////////////////////////////////////////////////////////
// Keyboard
keyButtons = 12.collect { |i|
	var btnColor;
	if ([0, 2, 4, 5, 7, 9, 10].includes(i),
		{ btnColor = "#6b554d" },
		{ btnColor = "#c0a5a1" }
	);
	Button.new()
	.minSize_(Size(20, 40))
	.states_([[i, Color.white, Color.fromHexString(btnColor)]])
	.mouseDownAction_({|button|
		oscAddr.sendMsg("/web/note/velocity", volumeSlider.value);
		oscAddr.sendMsg("/web/note/note_on", 60+i);
	})
	.action_({|button|
		oscAddr.sendMsg("/web/note/note_off", 60+i);
	});
};
keyboardLayout = HLayout.new(*keyButtons);

///////////////////////////////////////////////////////////////////
// Main Layout
upperLayout = HLayout.new(
	[panelLayout, stretch: 2],
	[volumeLayout],
	[knobsLayout, stretch: 1.5]
);
mainLayout = VLayout.new(upperLayout, keyboardLayout);

///////////////////////////////////////////////////////////////////
// Display
w.layout = mainLayout;
w.front;

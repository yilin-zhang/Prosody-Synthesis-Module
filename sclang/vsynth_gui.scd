// Color palette: https://www.color-hex.com/color-palette/91866

var emotionPanel, paramKnobs, keyButtons, velocitySlider;
var mainLayout, upperLayout;
var panelLayout, knobsLayout, knobLayouts, keyboardLayout, velocityLayout;
var panelText, vcoText, knobTexts, velocityText;
var oscAddr;

var velocity=1.0;

Window.closeAll;
w = Window.new("Prosody Synthesis Control Panel", Rect(500, 200, 380, 250))
.background_(Color.fromHexString("#e9dbd5"));
oscAddr = NetAddr.new("127.0.0.1", 8088);

///////////////////////////////////////////////////////////////////
// Emotion Panel
emotionPanel = Slider2D.new()
.background_(Color.fromHexString("#c0a5a1"))
.x_(0.5).y_(0.5)
.action_({|panel|
	oscAddr.sendMsg("/gui/emotion/valence", panel.x.linlin(0.0, 1.0, -1.0, 1.0));
	oscAddr.sendMsg("/gui/emotion/power", panel.y.linlin(0.0, 1.0, -1.0, 1.0));
});
panelText = StaticText.new().string_("Valence × Power");
panelLayout = VLayout.new([panelText, align: \center], emotionPanel);

///////////////////////////////////////////////////////////////////
// Velocity Slider
velocitySlider = Slider.new()
.background_(Color.fromHexString("#a68886")).value_(1.0);
velocityText = StaticText.new().string_("Velocity");
velocityLayout = VLayout.new([velocityText, align: \center], velocitySlider);

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
	oscAddr.sendMsg("/gui/feature/tune", knob.value.linlin(0.0, 1.0, -1.0, 1.0));
});
paramKnobs[1]
.value_(0.3)  // Vibrato 0.3
.action_({|knob|
	oscAddr.sendMsg("/gui/feature/vibrato", knob.value);
});
paramKnobs[2]
.value_(1)    // Brightness 1.0
.action_({|knob|
	oscAddr.sendMsg("/gui/feature/brightness", knob.value);
});
paramKnobs[3]
.action_({|knob|
	oscAddr.sendMsg("/gui/feature/noisiness", knob.value);
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
	if ([0, 2, 4, 5, 7, 9, 11].includes(i),
		{ btnColor = "#c0a5a1" },
		{ btnColor = "#6b554d" }
	);
	Button.new()
	.minSize_(Size(20, 40))
	.states_([[i, Color.white, Color.fromHexString(btnColor)]])
	.mouseDownAction_({|button|
		oscAddr.sendMsg("/gui/note/velocity", velocitySlider.value);
		oscAddr.sendMsg("/gui/note/note_on", 60+i);
	})
	.action_({|button|
		oscAddr.sendMsg("/gui/note/note_off", 60+i);
	});
};
keyboardLayout = HLayout.new(*keyButtons);

///////////////////////////////////////////////////////////////////
// Main Layout
upperLayout = HLayout.new(
	[panelLayout, stretch: 2],
	[velocityLayout],
	[knobsLayout, stretch: 1.5]
);
mainLayout = VLayout.new(upperLayout, keyboardLayout);

///////////////////////////////////////////////////////////////////
// Display
w.layout = mainLayout;
w.front;

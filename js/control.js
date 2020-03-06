let osc = new OSC();
osc.open(); // connect by default to ws://localhost:8080

document.getElementById('send').addEventListener('click', () => {
    let message = new OSC.Message('/test/random', Math.random());
    osc.send(message);
});

//////////////////////////////////////////////////////////
// VCO sliders
let slider_vco_1 = document.getElementById("VCO1");
slider_vco_1.addEventListener('input', () => {
    let message = new OSC.Message('/web/vco/1', slider_vco_1.value/100);
    osc.send(message);
});

let slider_vco_2 = document.getElementById("VCO2");
slider_vco_2.addEventListener('input', () => {
    let message = new OSC.Message('/web/vco/2', slider_vco_2.value/100);
    osc.send(message);
});

//////////////////////////////////////////////////////////
// Keyboard
let key_60 = document.getElementById("key-60");
key_60.addEventListener('mousedown', () => {
    let msg_velocity = new OSC.Message('/web/note/velocity', 1.);
    let msg_note_on = new OSC.Message('/web/note/note_on', 60);
    osc.send(msg_velocity);
    osc.send(msg_note_on);
});
key_60.addEventListener('mouseup', () => {
    let msg_note_off = new OSC.Message('/web/note/note_off', 60);
    osc.send(msg_note_off);
});



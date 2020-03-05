let osc = new OSC();
osc.open(); // connect by default to ws://localhost:8080

document.getElementById('send').addEventListener('click', () => {
    let message = new OSC.Message('/test/random', Math.random());
    osc.send(message);
});

//////////////////////////////////////////////////////////
// VCO sliders
let slider_vco_1 = document.getElementById("VCO1")
slider_vco_1.addEventListener('input', () => {
    let message = new OSC.Message('/vsynth/vco/1', slider_vco_1.value/100);
    osc.send(message);
})

let slider_vco_2 = document.getElementById("VCO2")
slider_vco_2.addEventListener('input', () => {
    let message = new OSC.Message('/vsynth/vco/2', slider_vco_2.value/100);
    osc.send(message);
})
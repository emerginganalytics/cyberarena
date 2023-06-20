/* Functions to update CSS props */

function updateRpm (value) {
	document.querySelector('#revmeter .gauge').style.setProperty('--rpm', value);
}

function updateMph (value) {
	document.querySelector('#speedmeter .gauge').style.setProperty('--mph', Math.round(value));
	speedTrap(Math.round(value))
}

function updateGear (value) {
	document.querySelector('#revmeter .gauge').style.setProperty('--gear', value);
}


/* Binding functions for manual control of CSS props from inputs */
const rpmControl = document.querySelector('input[name=rpm]');

rpmControl.addEventListener('keyup', function() { updateRpm(this.value); });
rpmControl.addEventListener('input', function() { updateRpm(this.value); });


const mphControl = document.querySelector('input[name=mph]');

mphControl.addEventListener('keyup', function() { updateMph(this.value); });
mphControl.addEventListener('input', function() { updateMph(this.value); });


const gearControl = document.querySelector('input[name=gear]');

gearControl.addEventListener('keyup', function() { updateGear(this.value); });
gearControl.addEventListener('input', function() { updateGear(this.value); });



/* Driving simulation */

let speed = 0;
let revs = 750;
let gear = 0;
let _prevGear = 0;
let gas = 0;
const idleRevs = 0;
const revLimiter = 6700;
const topGear = 6;
const minGearRatio = 24;
const maxGearRatio = 100;
const gearRatios = [ 0, 125, 78, 47, 34, 27, 24 ].map(i => i ? 1/i : i);
const thresholds = 'low'


function gearUp () {
	if (gear < topGear) {
		_prevGear = gear;
		gear++;
	}
	gearControl.value = gear;
	updateGear(gear);
}

function gearDown () {
	if (gear) {
		_prevGear = gear;
		gear--;
	}
	gearControl.value = gear;
	updateGear(gear);
}

function speedDown () {
	if (speed > 0) {
		speed = Math.max(speed-1, 0);
	}
}

function calculateSpeed () {
	if (gear) {
		speed = (gearRatios[ gear ] * revs) * 0.6213711922;
	}
	else {
		speedDown();
	}

	mphControl.value = speed;
	updateMph(speed);
}

function calculateRevsFromSpeed () {
	if (gearRatios[ gear ]) {
		revs = (speed / 0.6213711922) / gearRatios[ gear ];
		if (revs < idleRevs) {
			revs = idleRevs;
			if (_prevGear) {
				_prevGear = gear;
				gear = 0;
			}
			gearControl.value = gear;
			updateGear(gear);
			updateRpm(revs);
		}
	}
}

const to = setInterval (() => {
	if (gas) {
		if (revs < revLimiter) {
			revs += (1 - Math.random()) * 200 + (gearRatios.length - gear) * 100;
		}
		else {
			if (revs < idleRevs) {
				revs = idleRevs;
			}
			else {
				revs-=300;
			}
		}
	}
	else {
		if (gear) {
			speedDown();
			calculateRevsFromSpeed();
		}
		else {
			if (revs > idleRevs) {
				revs-= (1 - Math.random()) * 200 + 200;
			}
		}
	}

	rpmControl.value = revs;
	updateRpm(revs);
	calculateSpeed();
}, 100);



const throttleButton = document.querySelector('button[name=throttle]');

throttleButton.addEventListener('mousedown', () => gas = 1);
throttleButton.addEventListener('mouseup', () => gas = 0);

const gearUpButton = document.querySelector('button[name="gear-up"]');
const gearDownButton = document.querySelector('button[name="gear-down"]');

gearUpButton.addEventListener('click', gearUp);
gearDownButton.addEventListener('click', gearDown);


const gearControls = Array.from(document.querySelectorAll('input[type=range][name^=gear]'));


gearControls.forEach((gearControl, index) => {
	gearRatios[index+1] = 1 / Number.parseInt(gearControl.value, 10);

	gearControl.addEventListener('input', function(){
		let value = Number.parseInt(this.value, 10);
		const minValue = Number.parseInt(this.dataset.min, 10);
		const maxValue = Number.parseInt(this.dataset.max, 10);

		if (value < minValue) {
			this.value = minValue;
			value = minValue;
		}
		if (value > maxValue) {
			this.value = maxValue;
			value = maxValue;
		}


		if (index) {
			gearControls[index-1].dataset.min = value+1;
		}
		if (index < gearControls.length-1){
			gearControls[index+1].dataset.max = value-1;
		}

		gearRatios[index+1] = 1/value;
		this.nextElementSibling.textContent = `1/${value}`;
	});
});

function speedTrap(value) {
	let device_id = getDeviceID()
	let low, mid, sus, sirens;
	low = 20;
	mid = 50;
	sus = 90;
	sirens = 160;
	if (( value === low)){
		// send teal;
		send_command('teal', device_id, '/iot/commands/' + device_id + '/submit');
	} else if (value === mid){
		// send purple
		send_command('purple', device_id, '/iot/commands/' + device_id + '/submit');
	} else if (value === sus ){
		// send red; red is sus
		send_command('red', device_id, '/iot/commands/' + device_id + '/submit');
	} else if (value > sirens){
		// break out those spike strips, baby!
		send_command('CRITICAL', device_id, '/iot/commands/' + device_id + '/submit');
	}
}
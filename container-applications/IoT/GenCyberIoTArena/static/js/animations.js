/*<div class="animated-text" id=animated-text">
                <i>C</i><i>o</i><i>n</i><i>n</i><i>c</i><i>t</i><i>i</i><i>n</i><i>g</i><i>
                </i><i>.</i><i>.</i><i>.</i><i>.</i>
            </div>
       */

function diagonalWipe(elementID) {
    /* Adds Diagonal Wipe effect to specified element */
    var targetElement = document.getElementById(elementID);
    $(targetElement).find("input").hide();  //.id("iot-device-input").hide();
    $(targetElement).find("button").hide(); //.id("iot-device-input-btn").hide();
    targetElement.style.border = 'none';
    targetElement.classList.add('gradient-wipe');
    targetElement.style.background = '#1a73e8';

    showAnimatedText();

    // the children().fadeOut line is also hiding the connecting animation. Need to figure
    // out a way around this.
    // Change the color on the animation text to work with the blue background. Maybe just white
    // with a little gold?
}
function showAnimatedText() {
    var tempDiv = document.createElement("div");
    tempDiv.classList.add('animated-text-div');
    tempDiv.innerHTML = '<i>C</i><i>o</i><i>n</i><i>n</i><i>e</i><i>c</i><i>t</i><i>i</i><i>n</i><i>g</i><i>\n' +
        '                </i><i>.</i><i>.</i><i>.</i><i>.</i>';
    var animatedTextDiv = document.getElementById("animated-text-div");
    animatedTextDiv.appendChild(tempDiv);
}

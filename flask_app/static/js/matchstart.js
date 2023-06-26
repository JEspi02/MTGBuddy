// Lifepoints
const lifepointsElement = document.getElementById('lifepoints-counter');
let lifepoints = 20;

// Lifepoints buttons
const minus5Button = document.getElementById('minus-5-lifepoints');
const minus1Button = document.getElementById('minus-1-lifepoints');
const plus1Button = document.getElementById('plus-1-lifepoints');
const plus5Button = document.getElementById('plus-5-lifepoints');

minus5Button.addEventListener('click', () => {
    updateLifepoints(-5);
});

minus1Button.addEventListener('click', () => {
    updateLifepoints(-1);
});

plus1Button.addEventListener('click', () => {
    updateLifepoints(1);
});

plus5Button.addEventListener('click', () => {
    updateLifepoints(5);
});

function updateLifepoints(change) {
    lifepoints += change;
    lifepointsElement.textContent = lifepoints;
}

// Dice roll
const rollDiceButton = document.getElementById('roll-dice');
const diceResultElement = document.getElementById('dice-result');

rollDiceButton.addEventListener('click', () => {
    const diceTypeElement = document.getElementById('dice-type');
    const diceType = parseInt(diceTypeElement.value);
    const diceRollResult = Math.floor(Math.random() * diceType) + 1;
    diceResultElement.textContent = `Dice Roll Result: ${diceRollResult}`;
});

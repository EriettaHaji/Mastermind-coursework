var serviceUrl = 'http://playMastermind.pythonanywhere.com';
var clickedPeg;
var clickedSlot;
var numCols;
var tries;
var ctries;
var codeLength;


function addTryRow() {
    /**
     * Adds a new row for a new attempt
     */
    if(ctries >= tries) {
        return ;
    }
    const board = document.getElementById('game-board');
    const dTry = document.createElement('div');
    dTry.classList.add('try');

    // add slots
    ++ctries;
    for(let i=0; i<codeLength; i++) {
        const slot = document.createElement('div');
        slot.classList.add('slot');
        slot.setAttribute('id', `slot-${ctries}-${i}`);
        slot.addEventListener('click', slotOnClick, false);
        dTry.appendChild(slot);
    }

    // add hint
    const dHint = document.createElement('div');
    dHint.classList.add('hint');

    const isOdd = codeLength % 2 === 0 ? false : true;
    const r = Math.floor(codeLength/2);
    for(let i=0; i<r; i++) {
        const d = document.createElement('div');
        d.appendChild(document.createElement('span'));
        d.appendChild(document.createElement('span'));

        dHint.appendChild(d);
    }
    if(isOdd) {
        // add the extra row
        const d = document.createElement('div');
        d.appendChild(document.createElement('span'));

        dHint.appendChild(d);
    }

    dTry.appendChild(dHint);
    board.appendChild(dTry);

}
function slotOnClick(e) {
    // 1. get the currently selected peg
    // 2. get its color and value and assign to slot
    if(!clickedPeg) {
        return console.log('[-] No peg selected');
    }
    const slot = e.target;
    const { color, value } = clickedPeg;
    slot.setAttribute('data-color', color);
    slot.setAttribute('data-value', value);


    slot.style.backgroundColor = color.startsWith('#') ? color : `#${color}`;
}

function pegOnClick(e) {
    // 1. save the color of the peg
    const peg = e.target;
    const [ color, value ] = [
        peg.getAttribute('data-color'),
        peg.getAttribute('data-value')
    ];
    if(!clickedPeg) {
        clickedPeg = { color, value };
    } else {
        if(clickedPeg.color !== color) {
            clickedPeg = { color, value };
        }
    }
}

function updateHighlights(blacks, whites) {
    /**
     * Add the results in the top div
     */
    const upd = document.getElementById('game-updates');
    if(blacks === codeLength && whites === 0) upd.innerHTML = 'You Won!!!';
    else upd.innerHTML = `Blacks: ${blacks}  Whites: ${whites}`;
}
function updateScore(node, blacks, whites) {
    /**
     * Update the score for the last attempt
     */
    const children = node.getElementsByTagName('span');
    let i = 0;
    let cw = 0;
    let cb = 0;

    while(i < children.length && cb++ < blacks) {
        const c = children[i++];
        c.style.backgroundColor = `#000000`;
    }

    while(i < children.length && cw++ < whites) {
        const c = children[i++];
        c.style.backgroundColor = `#ffffff`;
    }
}

async function checkGuess() {
    /**
     * Checks a guess by sending it to the
     * server
     */
    const board = document.getElementById('game-board');
    const slots = document.getElementsByClassName('slot');
    // get all slots for the current try
    const current = Array.prototype.filter.call(slots, slot => {
        const id = slot.getAttribute('id');
        return id.startsWith(`slot-${ctries}`) ? true : false;
    });
    //console.log('current', current);
    const guess = current.map(slot => {
        let v = slot.getAttribute('data-value');
        // if there are more pegs than colors
        // then add -1 for all pegs that are kept blank
        if(typeof v === 'string' && v.length >= 1) v = parseInt(v);
        else v = -1;
        return v;
    });
    //console.log('Guess', guess);
    try {
        // call '/check' route from server.py
        const url = serviceUrl.concat('/check')
        const res = await fetch(url, {
            body: JSON.stringify({
                guess
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            cache: 'no-cache',
            method: 'post'
        });
        const json = await res.json();
        if(json.error) {
            console.log('[x] Error: ' + json.error);
        } else {
            //console.log('Response', json);
            // update the last hint
            const lastRow = board.lastElementChild;
            //console.log('last', lastRow);

            updateScore(lastRow, json.blacks, json.whites);
            updateHighlights(json.blacks, json.whites);

            if(json.result === 'incorrect') {
                // add another row
                addTryRow();
            }
        }
    } catch(HttpError) {
        console.log('[x] Error sending http request');
        console.error(HttpError);
    }

}

async function getHint() {
    /**
     * Gets a hint from the server
     */
    try {
        const hd = document.getElementById('hint-display');
        hd.innerHTML = '';
        // call '/hint' route from server.py
        const url = serviceUrl.concat('/hint')
        const res = await fetch(url, {
            method: 'GET',
            credentials: 'same-origin',
            cache: 'no-cache',
        });
        const { hint } = await res.json();
        // set hint
        const colors = Array.from(document.getElementsByClassName('palette-color'));
        let l;
        hint.map(h => {
            let el =  colors.find(c => parseInt(c.getAttribute('data-value')) === h);
            if(!el) {
                // this color is not in the palette
                // in this case, the best option to
                // randomly select a color from the existing
                // palette
                const idx = Math.floor(Math.random() * colors.length);
                console.log('Colors', colors.length, 'idx', idx, 'colors[idx]', colors[idx]);
                return colors[idx].getAttribute('data-color');
            }
            return el.getAttribute('data-color');
        }).map(c => {
            const el = document.createElement('div');
            el.classList.add('hint-color');
            el.style.backgroundColor = `${c}`;
            return el;
        }).forEach(el => hd.appendChild(el));

    } catch(HttpError) {
        console.error(HttpError);
    }

}

function init() {
    const slots = document.getElementsByClassName('slot');
    const pegs = document.getElementsByClassName('palette-color');
    const checkBtn = document.getElementById('check-btn');
    const hintBtn = document.getElementById('hint-btn');
    numCols = parseInt(document.querySelector("input[name='numCol']").value);
    tries = parseInt(document.querySelector("input[name='tries']").value);
    codeLength = parseInt(document.querySelector("input[name='codeLength']").value)
    ctries = 0;

    Array.prototype.forEach.call(slots, slot => {
        slot.addEventListener('click', slotOnClick, false);
    });
    Array.prototype.forEach.call(pegs, peg => {
        peg.addEventListener('click', pegOnClick, false);
    });

    checkBtn.addEventListener('click', checkGuess, false);
    hintBtn.addEventListener('click', getHint, false);
}

init();

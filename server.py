import math
import random
# jsonify, g,

from flask import (
    Flask, request, redirect, url_for, render_template,
    session
)
import game as Game

#reference: https://docs.python.org/3/library/datetime.html
#Needed to set an expiration for the session
from datetime import timedelta
SESSION_EXPIRY = 5      # a session will live for 5 mins

# create our flask application as server
server = Flask(__name__, static_folder='static')

# use templates to return html pages
@server.route('/')
def home():
    return render_template('home.html')

#decorator for each one of the pages (i.e. actions) of the application
@server.route('/play', methods=['GET', 'POST'])
def play():
    print(request.args)
    if request.method == 'GET':
        # render the template to setup the game
        return render_template('game_setup.html')
    elif request.method == 'POST':
        url = url_for(
            'playMastermind',
            numCol=request.form.get('numCol'),
            codeLength=request.form.get('codeLength'),
            duplicate=request.form.get('duplicate')
        )

        return redirect(url)

# shortcut for route() with methods=["GET"]
@server.get('/playMastermind')
def playMastermind():
    # i will be used for the extra colors that may be needed in the colors dictionary
    i = 0
    numCol = int(request.args.get('numCol', None))
    codeLength = int(request.args.get('codeLength', None))
    duplicate = request.args.get('duplicate', None)
    duplicate = True if duplicate and duplicate == 'yes' else False

    if not numCol or not codeLength:
        # error: 400 means the request of the client is incorrect or corrupt, and the server can't understand it
        return { 'error': 'Arguments not found' }, 400

    code = Game.createCode(numCol, codeLength, duplicate)
    # create list S with all posible codes at the beginning of the game
    S = Game.createS(codeLength, numCol)
    # generate the required number of unique colors for each unique digit in code
    # create a dictionary and use that in the template
    colors = {}
    for digit in code:
        if not digit in colors:
            colors['{}'.format(digit)] = Game.getColor(digit)
    # for example if code is (5, 6, 1, 4)
    # colors will be {'5': '#FF8C00', '6': '#8B008B', '1': '#FF0000', '4': '#FFD700'}
    # reference: https://www.w3schools.com/python/ref_string_format.asp

    if numCol >= codeLength:
        # in this case you need to add extra colors in the palette
        extra_colors = abs(numCol - codeLength)
        while extra_colors > 0 or len(colors) < numCol:
            i = random.randint(1,6)
            if not i in code:
                color = Game.getColor(i)
                colors['{}'.format(i)] = color
                extra_colors = extra_colors - 1

    # add the code in HTTP only cookie
    # this will add the cookie to every request
    # and can be checked against later in every ohter route or function
    # reference: https://pythonbasics.org/flask-sessions/ and https://flask-session.readthedocs.io/en/latest/
    session['code'] = code
    session['numCols'] = numCol
    session['duplicate'] = duplicate
    session['codeLength'] = codeLength
    session['S'] = S
    # session is used to make accessible all of the above variables from every @app.route
    isOdd = True if codeLength % 2 != 0 else False
    hintRows = math.ceil(codeLength/2)

    return render_template(
        'game.html',
        numCol=numCol,
        codeLength=codeLength,
        duplicate=duplicate,
        rows=12,
        colors=colors,
        hintRows=hintRows,
        isOdd=isOdd,
        code=code
        )

# shortcut for route() with methods=["POST"]
@server.post('/check')
# the function will be called by game.js with AJAX call when the check button is pressed
def check_guess():
    # checks a guess submitted by the user
    # session should contain 'code', 'numCol' etc
    if not 'code' in session or \
        not 'numCols' in session or \
            not 'codeLength' in session:
                return { 'error': 'No session', }
    # get guess in json format (JSON is a data-interchange language)
    # json string is the input from game.js
    guess = request.json.get('guess')

    # retrieve codeLength and code from session
    codeLength = session['codeLength']
    code = session['code']

    if not guess:
        return { 'error': 'Bad Request' }

    # call checkGuess to get score
    blacks, whites = Game.checkGuess(guess, code)

    # res is dictionary to contain result, blacks and whites. Will be used to display results
    res = {}
    if blacks == codeLength:
        # guessed correctly
        res['result'] = 'correct'
    else:
        res['result'] = 'incorrect'
        # retrieve S from session
        S = session['S']
        # execute removeS() to remove all codes which do not give the same result with score if guess was the code
        S = Game.removeS(S,code,guess)
        # store the new, reduced S to session
        session['S'] = S

    res['whites'] = whites
    res['blacks'] = blacks

    return res

'''
# '/hint' before testing
@server.get('/hint')
def hint():
    codeLength = session['codeLength']
    numCols = session['numCols']

    try:
        lastHints = session['hints']
    except KeyError:
        lastHints = None


    s = Game.createS(codeLength, numCols)
    h = None

    if lastHints:
        # this hint was already provided
        # so remove it from S so it is not repeated
        for k in range(len(lastHints)):
            lastHint = lastHints[k]
            #print('removing {} from s'.format(lastHint))
            found = True
            for idx, code in enumerate(s):
                #print('code', code)
                for i in range(len(code)):
                    if code[i] != lastHint[i]:
                        found = False
                        break
                if found:
                    #print('found {} at {}'.format(lastHint, idx))
                    s.pop(idx)
                    break
                else:
                    found = True

        h = Game.giveHint(S=s)
        lastHints.append(h)
        session['hints'] = list(lastHints)

    else:
        h = Game.giveHint(S=s)
        session['hints'] = [h]

    return {
        'hint': h
    }

'''

# '/hint' after testing
@server.get('/hint')
# the function will be called by game.js with AJAX call when the hint button is pressed
def hint():
    # retrieve S from session
    S = session['S']
    # if in list S there is only one remaining element, this will be the hint
    if (len(S)==1):
        h=S[0]
    # else, call giveHint function to get best next guess
    else:
        h = Game.giveHint(S)

    return {
        'hint': h
    }

@server.route('/minimax')
def minimax():
    return render_template('minimax.html')


server.secret_key = 'SECReT'
server.config['SESSION_TYPE'] = 'filesystem'
server.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=SESSION_EXPIRY)

if __name__ == '__main__':
    server.run()

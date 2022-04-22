
# *** GENERATE CODE ***
#import random module to generate random numbers for the code
import random
#The generateCode() function will be called by the createCode() and return a list of random numbers
def generateCode(numCol, codeLength):
    code = []
    for i in range(codeLength):
        n = random.randint(1,numCol)
        code.append(n)
    return code
#The createCode() function will be called by the main Mastermind program
def createCode(numCol, codeLength, duplicates):
    if (numCol<codeLength) and (not duplicates):
        duplicates = True
    code = generateCode(numCol,codeLength)
    #Convert the list to a set to decide whether there are duplicates in the list
    codeSet = set(code)
    if duplicates:
        #if duplicates allowed, the code is OK
        return code
    else:
        #if duplicates are not allowed, the generateCode() function will be called until there are no duplicates in the list
        while len(code)!=len(codeSet):
            code = generateCode(numCol,codeLength)
            codeSet = set(code)
        return code

# *** CHECK CODE ***
# checkGuess() accepts two inputs (guess, code) and returns number of blacks and number of whites
def checkGuess(guess,code):
    n = len(code)
    # Determine the correct and incorrect positions.
    # Create new list for correct positions
    correct_positions = [i for i in list(range(n)) if guess[i] == code[i]]
    # Create new list for incorrect positions
    incorrect_positions = [i for i in list(range(n)) if guess[i] != code[i]]
    # blacks is the length of correct positions
    blacks = len(correct_positions)
    # remove the correct positions from the two lists and see what is left
    left_guess = [guess[i] for i in incorrect_positions]
    left_code = [code[i] for i in incorrect_positions]
    # Create the common values between the two new lists.
    common_values = set(left_guess) & set(left_code)
    # Determine the number of transposed values.
    whites = 0
    for x in common_values:
        # If a transposed common number in the two lists is more than once,
        # the program will increase by the minimum frequency this number is presented.
        whites = whites + min(left_guess.count(x), left_code.count(x))
    return blacks, whites

# *** GET COLOR ***
# accepts digit and return color in hexadecimal format

def getColor(digit):
    colors = {
        '1': '#FF0000',
        '2': '#00FF00',
        '3': '#0000FF',
        '4': '#FFD700',
        '5': '#FF8C00',
        '6': '#8B008B'
    }

    try:
        return colors['{}'.format(digit)]
    except KeyError:
        return None

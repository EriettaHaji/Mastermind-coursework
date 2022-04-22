# *** S LIST OF ALL POSSIBLE CODES ***
# import itertools to easily create the list of all possible values
import itertools
import random
# createS() is called by main program, creates list S of all possible codes
def createS(codeLength, numCol):
    S = [tuple(x) for x in itertools.product(range(1,numCol+1), repeat = codeLength)]
    return S

# import input.py to use check_guess() to get the score of a guess
from .input import *
# removeS() is called by main program every time the user asks for hint,
# removeS() removes from S any code with different score than the guess's score
def removeS(S,code,guess):
    print(f"Remove from S all codes with different score than {guess}. Code is {code}")
    score = checkGuess(guess, code)
    print (f"score for {guess} is {score}")
    newS=[]
    for x in S:
        # check_guess will be called to decide score for every x in S
        if (score == checkGuess(x,guess)):
            # if the score is the same, the x will remain in the new S list
            newS.append(x)
    return newS

# *** MINIMAX ALGORITHM ***
'''
Minimax works as follows: For every code c in S calculate rank
and select next guess the code with minimum rank.
Rank is the maximum times a score is present
if every other code g in S considers c as the real code
'''
def countFrequency(scoreList):
    # Create an empty dictionary (key will be the score, value will be is its frequency in scoreList)
    freq={}
    # If a score from scoreList appears for the first time, set its value (frequency) to 1
    # Otherwise increase value (frequency) by 1
    for item in scoreList:
        if (item in freq):
            freq[item] +=1
        else:
            freq[item] = 1
    return (max(freq.values()))

# findMiniMax() is called by the giveHint() function
def findMiniMax(S):
    # rankList is the dictionary of ranks (values) of the codes (keys) in the S list
    rankList={}
    for c in S:
        # For every code c in S create a list of scores which will be produced
        # if every other code g in S considers c as real code
        scoreList=[]
        for g in S:
            if c!=g:
                score = checkGuess(g,c)
                # The scoreList will keep all scores produced.
                scoreList.append(score)
        # CountFrequency() will return the rank for each code in S.
        # Rank for each code c will be the maximum number a score is produced
        # if every other code considers c as real code
        # len(S) - rank will be the number of the codes eliminated if c is selected as next guess.
        rank = countFrequency(scoreList)
        #print (f"max rank for {c} is {rank}")
        # Import new item in rankList (c is the key and rank is the value)
        rankList[c] = rank
    #print(f"list of ranks of all codes is {rankList}")
    # Find minimum rank
    print(f"min is {min(rankList.values())}")
    # Get the key (code) which has the minimum rank
    nextGuess = min (rankList, key=rankList.get)
    print(f"next guess could be {nextGuess}")
    return nextGuess

# giveHint() function is called from the main program to decide the next best guess
def giveHint(S):
    # findMiniMax() will decide the next best guess among the list S
    nextGuess = findMiniMax(S)
    return nextGuess

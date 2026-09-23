'''

This script uses the Markov chain saved as a Python dictionary of dictionaries (smbprobabilities.pickle) to generate a new
level
'''

import sys
import os
import random
import pickle

#Load up the probability dictionary(s)
markovProbabilities_L = pickle.load(open("smbprobabilities_L.pickle", "rb"))
markovProbabilities_S = pickle.load(open("smbprobabilities_S.pickle", "rb"))
markovProbabilities = markovProbabilities_L | markovProbabilities_S

level = {}

#Parameters determining the size of the level
num_levels = 20  # Generate X many levels in one generate
maxY = 14  # will end up generating a level with one height larger than this
maxX = 100
markov_conversion_percent = 0.8  # The X percentage of height needed before we convert to the "S" markov chain. A value of 0.8 would mean 80% (starting from the bottom) would be L, followed by 20% S at the top.
bias = 0.15 # adjusts how much the gradient function will add content (higher numbers = more output)
weight = 0.25 # adjusts how much the gradient function affects generation

# Helper function to insert a tile at a specific index
def replaceTile(x, y, tile):
    temp = level[y]
    return temp[:x] + tile + temp[x + 1:]


# Saves a level as a .txt with a name
def save_file(filename):
    # Save the generated level to a file
    outputFile = open(os.path.join(os.getcwd(), "Generated Levels", filename + ".txt"), 'w')
    for y in range(0, maxY + 1):
        outputFile.write(level[y] + "\n")
    outputFile.close()


# Removes any blocks not within one square (including diagonals!)
def remove_floating_blocks():
    for y in range(0, maxY):
        for x in range(0, maxX):
            currentTile = level[y][x]
            tileLeft = tileRight = tileAbove = tileBelow = tileUpLeft = tileUpRight = tileDownLeft = tileDownRight = "-"

            if x > 0:
                tileLeft = level[y][x - 1]
            if x < maxX - 1:
                tileRight = level[y][x + 1]
            if y > 0:
                tileAbove = level[y - 1][x]
            if y < maxY:
                tileBelow = level[y + 1][x]
            if x > 0 and y > 0:
                tileUpLeft = level[y - 1][x - 1]
            if x < maxX - 1 and y > 0:
                tileUpRight = level[y - 1][x + 1]
            if x > 0 and y < maxY:
                tileDownLeft = level[y + 1][x - 1]
            if x < maxX - 1 and y < maxY:
                tileDownRight = level[y + 1][x + 1]

            # If there is a random floating tile in the middle of nowhere, remove it.
            if currentTile not in ("-", "o",
                                   "?") and tileAbove == tileBelow == tileRight == tileLeft == tileUpLeft == tileUpRight == tileDownLeft == tileDownRight == "-":
                level[y] = replaceTile(x, y, "-")


# Takes all floating enemies and moves them to the nearest optimal location
def replace_floating_enemies():
    availableEnemies = 0  # if we remove any enemies, add to the counter and place them at the next available spot
    for y in range(0, maxY):
        for x in range(0, maxX):
            currentTile = level[y][x]
            tileBelow = "-"

            if y < maxY:
                tileBelow = level[y + 1][x]

            # If there is an enemy floating in the air or sitting on top of another enemy, remove it
            if currentTile == "E" and tileBelow in ("-", "E"):
                level[y] = replaceTile(x, y, "-")
                availableEnemies += 1

            # Place an enemy on the nearest tile if we have one ready and there's a place for them
            if availableEnemies > 0 and currentTile == "-" and tileBelow in ("X", "S"):
                level[y] = replaceTile(x, y, "E")
                availableEnemies -= 1


# Replaces the enemies and removes floating blocks
def post_processing():
    replace_floating_enemies()
    remove_floating_blocks()


# Checks the markov chains for any matching states
def find_states(level, x, y):
    # Grab the current state, the three dependent values
    west = " "
    southwest = " "
    south = " "

    if x > 0:
        west = level[y][x - 1]
    if y < maxY:
        south = level[y + 1][x - 1]
    if x > 0 and y < maxY:
        southwest = level[y + 1][x]

    left = " "
    second_left = " "
    third_left = " "

    if x > 0:
        left = level[y][x - 1]
    if x > 1:
        second_left = level[y][x - 2]
    if x > 2:
        third_left = level[y][x - 3]

    stateL = west + southwest + south
    stateS = left + second_left + third_left
    return stateL, stateS


def get_token(stateL, stateS, y, maxY):
    # Basic function to make more things spawn at lower y levels, and less at higher y levels
    gradient = (((maxY - y) / maxY) - bias) * weight
    gradient_weighted = random.random() + gradient

    # Used for determining when we need to switch from L to S
    height_percent = y / maxY

    useStateL = None  # variable to determine which state we will use
    stateLMatch = stateL in markovProbabilities_L.keys()
    stateSMatch = stateS in markovProbabilities_S.keys()

    # Always return a state rather than nothing if at all possible
    if stateSMatch and not stateLMatch:
        useStateL = False
    if stateLMatch and not stateSMatch:
        useStateL = True
    if stateSMatch and height_percent >= markov_conversion_percent:  # switch from L to S at this height
        useStateL = False
    elif stateLMatch:
        useStateL = True

    currProb = 0

    # Run our calculations based on whatever dictionary we find our state in
    if useStateL is not None:
        markovProbabilities = markovProbabilities_L if useStateL else markovProbabilities_S
        state = stateL if useStateL else stateS
        for action in markovProbabilities[state]:
            currProb += markovProbabilities[state][action]
            if currProb > gradient_weighted:
                return action

    return "-"


# Generates a level with a filename at the end
def generate_level(iteration):
    # Starting in the bottom left corner, we begin the generation process, going bottom to top then left to right
    for y in range(maxY, -1, -1):
        level[y] = ""
        for x in range(0, maxX):  # We generate one tile at a time for each iteration of this inner loop
            stateL, stateS = find_states(level, x, y)
            tokenToUse = get_token(stateL, stateS, y, maxY)
            level[y] += tokenToUse  # Add the tile value (tokenToUse) to the level

    # Save a level without post processing, and another with post processing
    save_file("output" + "_" + str(iteration))
    post_processing()
    save_file("output_post_processing" + "_" + str(iteration))


# Generate however many levels (in this case 20)
for i in range(0, num_levels):
    generate_level(i)

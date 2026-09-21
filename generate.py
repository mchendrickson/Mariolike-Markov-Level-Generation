'''

This script uses the Markov chain saved as a Python dictionary of dictionaries (smbprobabilities.pickle) to generate a new
level
'''

import sys
import os
import random
import pickle

#Load up the probability dictionary
markovProbabilities_L = pickle.load(open("smbprobabilities_L.pickle", "rb"))
markovProbabilities_S = pickle.load(open("smbprobabilities_S.pickle", "rb"))
markovProbabilities = markovProbabilities_L | markovProbabilities_S

level = {}

#Parameters determining the size of the level
maxY = 20  #will end up generating a level with one height larger than this
maxX = 60


def replaceTile(x, y, tile):
    temp = level[y]
    return temp[:x] + tile + temp[x + 1:]


def save_file(filename):
    # Save the generated level to a file
    outputFile = open(os.path.join(os.getcwd(), "Generated Levels", filename + ".txt"), 'w')
    for y in range(0, maxY + 1):
        outputFile.write(level[y] + "\n")
    outputFile.close()


def generate_level(iteration):
    # Starting in the bottom left corner, we begin the generation process, going bottom to top then left to right
    for y in range(maxY, -1, -1):
        level[y] = ""
        for x in range(0, maxX):  #We generate one tile at a time for each iteration of this inner loop

            #Grab the current state, the three dependent values
            west = " "
            southwest = " "
            south = " "

            right = " "
            second_right = " "
            third_right = " "

            if x > 0:
                west = level[y][x - 1]
            if y < maxY:
                south = level[y + 1][x - 1]
            if x > 0 and y < maxY:
                southwest = level[y + 1][x]

            if x < len(level[y]) - 3:
                right = level[y][x + 1]
                second_right = level[y][x + 2]
                third_right = level[y][x + 3]

            stateL = west + southwest + south
            stateS = right + second_right + third_right

            stateSMatch = stateS in markovProbabilities.keys()
            stateLMatch = stateL in markovProbabilities.keys()

            #Query the Markov chain to see what tile value we should place at this tile location
            if stateLMatch or stateSMatch:
                # Weighted Sampling
                # Basic function to make more things spawn at lower y levels, and less at higher y levels
                weight = (maxY - y) / maxY
                gradient = random.random() + weight
                currProb = 0
                tokenToUse = "-"

                # pick between the L and S markov chain models, with more preference to S the higher we go
                if stateSMatch and stateLMatch:
                    state = stateL if random.random() < (y/maxY) else stateS
                elif stateLMatch and not stateSMatch:
                    state = stateL
                else:
                    state = stateS

                for action in markovProbabilities[state]:
                    currProb += markovProbabilities[state][action]
                    if currProb > gradient:
                        tokenToUse = action
                        break

                level[y] += tokenToUse  #Add the tile value (tokenToUse) to the level
            else:
                #If we can't find anything, just output an empty space
                level[y] += "-"

    save_file("output" + "_" + str(iteration))

    # Post-processing
    availableEnemies = 0 # if we remove any enemies, add to the counter and place them at the next available spot
    for y in range(1, maxY - 1):
        for x in range(1, maxX - 1):
            currentTile = level[y][x]
            tileLeft = level[y][x - 1]
            tileRight = level[y][x + 1]
            tileAbove = level[y - 1][x]
            tileBelow = level[y + 1][x]
            tileUpLeft = level[y - 1][x - 1]
            tileUpRight = level[y - 1][x + 1]
            tileDownLeft = level[y + 1][x - 1]
            tileDownRight = level[y + 1][x + 1]
            # If there is an enemy floating in the air or sitting on top of another enemy, remove it
            if currentTile == "E" and tileBelow in ("-", "E"):
                level[y] = replaceTile(x, y, "-")
                availableEnemies += 1
            # If there is a random floating tile in the middle of nowhere, remove it.
            if currentTile not in ("-", "o", "?") and tileAbove == tileBelow == tileRight == tileLeft == tileUpLeft == tileUpRight == tileDownLeft == tileDownRight == "-":
                level[y] = replaceTile(x, y, "-")
            # If there is an enemy floating in the air or sitting on top of another enemy, remove it (needed because we removed some tiles above)
            if currentTile == "E" and tileBelow in ("-", "E"):
                level[y] = replaceTile(x, y, "-")
                availableEnemies += 1
            # Place an enemy on the nearest tile if we have one ready and there's a place for them
            if availableEnemies > 0 and currentTile == "-" and tileBelow in ("X", "S"):
                level[y] = replaceTile(x, y, "E")
                availableEnemies -= 1

    save_file("output_post_processing" + "_" + str(iteration))


for i in range(0, 20):
    generate_level(i)

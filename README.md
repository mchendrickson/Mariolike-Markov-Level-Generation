# Mariolike Markov Level Generation (Modified)
An example of using a Markov chain to generate levels like those from Super Mario Bros. Based on the Markov chain given on the right and left sides of Figure 6.7

Scripts:

- train-L/S-shape.py: code that trains a Markov chain on the levels from Super Mario Bros. 1 and 2 (The Lost Levels) the S python file will create a markov chain based on the left size of figure 6.7, while L will train based on the right side. Both will be used in generate.py
- generate.py: code that generates new level(s) from the trained Markov chains, overwriting the existing level(s). It also does some post processing as well as applies a gradient function to reduce content as the height increases. 
- visualize.py: code that visualizes the generated level, as well as the level with post-processing with assets from Kenney's Platformer Asset Pack

To run the code take the following steps: 

1. Install Python 3.9-13 (but tweaking it for other versions should be simple) and the 'pickle' library
2. Run train.py, which will train two Markov chains (a standard straight line shape "S" and an "L" shape) represented as dictionaries based on the levels from Super Mario Bros. (SMB) and Super Mario Bros.: The Lost Levels (SMB2)
3. Run generate.py, which will generate a number of levels in a tile representation to Generated Level (Warning: this will overwrite any previous generated levels) This will generate a post-processed version, and a non post-processed version
4. (Optionally) run visualize.py, which will visualize the generated levels using Kenney's Pixel Platformer assets. 
5. Make alterations to train.py to alter the state representation of the Markov chain, generate.py to alter the sampling procedure, or visualize.py to alter the visualization procedure including the constructive rules, rereun steps 2-4 to see the impact of these changes

**Please note:** If you are running MacOS, you will need to replace the file load functions with backslashes instead of forward slashes! 

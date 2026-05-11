Welcome to my Honors Thesis Repository for, "Investigating Creative Possibility using Automated Composition."

My paper can be found online here: <link>

Run python file "CantusFirmusProducer.py" to generate a tree of all possible cantus firmi and potentially show the tree and show a random melody. Modify the call to produceCF at the very bottom to change the length of the desired melodies, the starting note (midi number) and whether to show the tree and a random melody.

Run python file "FirstSpeciesProducer.py" to generate tree of all possible first species counterpoints on a given cantus firmus and potentially show the tree and a random melody. Modify the call to produceFS at the very bottom to change the given melody and whether to show the tree and a random melody.

Run one of the ExperimentRunner python files to collect data for every possible first species counterpoint on every possible cantus firmus for a given length, or a sample of that space. These files generate a file named generated_melodies.txt with every cantus firmus for a length, then in a results folder writes a json output file for each cantus firmus

Experiment workflow:
0) create results folder
1) run ExperimentRunner to generate all cf or ExperimentRunner4 to selected 1000 random cf
2) if either gets cutoff, run ExperimentRunner3 to continue getting fs on previous generated_melodies.txt
3) once all data is acquired, rename results and generated_melodies to save them

HonorsThesis.ipynb was employed on google colab with mounted google drive for storage to increase speed and RAM memory for data collection. Data collection for length 16 got up to 80 GB RAM (This version is optimized to not store children in nodes, but further optimizations can be made). cflengthResults.csv contains estimates in the third column for the number of seconds each round of data collection took.

python file "DataAnalyzer.py" was used to read collected data and compile a csv with all relevant information for further data analysis

python file "CompareModels.py" was used to compare AIC scores for different models to fit several datasets and graph best fit lines on the data.

Notes:
- midi number in the code refers to ints that are representing notes in MIDI format

- musescore files created are stored in default temp folder on your computer

- counterpoint rules abridged by Dr. Christopher Adler of the University of San Diego

References:
- Music21 notation: https://www.music21.org/music21docs/ 
- Computer models of musical creativity, David Cope

Copyright Kian Drees, B.S. 
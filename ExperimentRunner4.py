"""run this program to generate all first species counterpoints on a random sample of 
specified size of cantus firmuses of specified length"""
from CantusFirmusProducer import CFProducer
from FirstSpeciesCP import FSProducer
import json
from music21 import *
import random
from wakepy import keep

N = 1000 #number of cf to find all fs on
LENGTH = 9 #length of cf (and therefore fs)
SEED = 0


def melodyToMidi(melody):
    melodyNotes = melody.split(",")
    returnMidi = []
    for notename in melodyNotes:
        returnMidi.append(note.Note(notename).pitch.midi)
    return returnMidi

random.seed(SEED)

print(f"Collecting data for {N} random cantus firmus of length {LENGTH} on seed {SEED}")

with keep.running():
    #every possible interval within an octave from a note
    every_possible_interval = list(range(-12, 13))  # semitones
    #possible intervals from each scale degree in a major scale (leaving out tritones and 7th intervals)
    MajorIntervalsFull = {
        1:  [ 2, 4, 5, 7, 9, 12, -1, -3, -5, -7, -8, -12, 0],
        2:  [ 2, 3, 5, 7, 12, -2, -3, -5, -7, -9, -12, 0],
        3:  [ 1, 3, 5, 8, 12, -2, -4, -5, -7, -9, -12, 0],
        4:  [ 2, 4, 7, 9, 12, -1, -3, -5, -8, -12, 0],
        5:  [ 2, 4, 5, 7, 9, 12, -2, -3, -5, -7, -8, -12, 0],
        6:  [ 2, 3, 5, 7, 8, 12, -2, -4, -5, -7, -9, -12, 0],
        7:  [ 1, 3, 5, 8, 12, -2, -4, -7, -9, 0]
    }
    #cantus firmus
    CFcomposer = CFProducer(every_possible_interval,MajorIntervalsFull)

    CFcomposer.produceCF(LENGTH,60,verbose=False)

    #run CFproducer and make a new file with only a random sample from that, then run the experiment on that 
    #read all data in
    with open("generated_melodies.txt","r") as f:
        content = f.read()
    #split content by \n
    content = set(content.split("\n"))
    with open("generated_melodies.txt","w") as f:
        for i in range(N):
            #get a random line from content and remove it
            line = random.choice(tuple(content))
            content.remove(line)
            f.write(line + "\n")

    #first species
    FScomposer = FSProducer(every_possible_interval,MajorIntervalsFull)
    with open("generated_melodies.txt","r") as f:
        for line in f:
            cfdict = json.loads(line.strip())

            #convert cf dict melody to list of music21 notes
            cf = melodyToMidi(cfdict["melody"])
            #print(cf)
            FScomposer.reset()
            FScomposer.produceFS(cf,verbose=False)
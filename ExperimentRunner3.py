"""Run this experiment to not generate new cf list but just use one already generated
this just add up everything already in results and skip to that line in generated melodies,
 so you can start where you left off if you ran 1 but closed it"""

from FirstSpeciesCP import FSProducer
import json
from music21 import *
from pathlib import Path
from wakepy import keep


def melodyToMidi(melody):
    melodyNotes = melody.split(",")
    returnMidi = []
    for notename in melodyNotes:
        returnMidi.append(note.Note(notename).pitch.midi)
    return returnMidi

print("Collecting data for cantus firmuses in generated_melodies.txt")

with keep.running(): #to keep cpu from turning off for running overnight
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

    file_count = sum(1 for p in Path("results").iterdir() if p.is_file())

    #first species
    FScomposer = FSProducer(every_possible_interval,MajorIntervalsFull)
    currLine = 0
    with open("generated_melodies.txt","r") as f:
        for line in f:
            
            currLine += 1
            if currLine <= file_count:
                continue

            cfdict = json.loads(line.strip())

            #convert cf dict melody to list of music21 notes
            cf = melodyToMidi(cfdict["melody"])
            #print(cf)
            FScomposer.reset()
            FScomposer.produceFS(cf,verbose=False)
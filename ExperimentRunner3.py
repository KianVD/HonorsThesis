"""This is a less memory intensive way to do ExperimentRunner2, just add up everything already in 
results and skip to that line ingenerated melodies"""

from CantusFirmusProducer import CFProducer
from FirstSpeciesCP import FSProducer
import json
from music21 import *
from pathlib import Path


def melodyToNotes(melody):
    melodyNotes = melody.split(",")
    returnNotes = []
    for notename in melodyNotes:
        returnNotes.append(note.Note(notename))
    return returnNotes

#every possible interval within an octave from a note
every_possible_interval = ["-P8", "-M7","-m7","-M6","-m6","-P5","-D5","-P4","-M3","-m3","-M2","-m2","P1","m2","M2","m3","M3","P4","D5","P5","m6","M6","m7","M7","P8"]#12 is middle
#possible intervals from each scale degree in a major scale (leaving out tritones and 7th intervals)
MajorIntervalsFull = {1:["M2","M3","P4","P5","M6","P8","-m2","-m3","-P4","-P5","-m6","-P8","P1"],
                    2:["M2","m3","P4","P5","P8","-M2","-m3","-P4","-P5","-M6","-P8","P1"],
                    3:["m2","m3","P4","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8","P1"],
                    4:["M2","M3","P5","M6","P8","-m2","-m3","-P4","-m6","-P8","P1"],
                    5:["M2","M3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-m6","-P8","P1"],
                    6:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8","P1"],
                    7:["m2","m3","P4","m6","P8","-M2","-M3","-P5","-M6","P1"] 
                    }

file_count = sum(1 for p in Path("results").iterdir() if p.is_file())

#first species
FScomposer = FSProducer(every_possible_interval,MajorIntervalsFull)
currLine = 0
with open("generated_melodies.txt") as f:
    for line in f:
        
        currLine += 1
        if currLine <= file_count:
            continue

        cfdict = json.loads(line.strip())

        #convert cf dict melody to list of music21 notes
        cf = melodyToNotes(cfdict["melody"])
        #print(cf)
        FScomposer.reset()
        FScomposer.produceFS(cf,verbose=False)
"""run this program to generate all first species counterpoints on a random sample of 
specified size of cantus firmuses of specified length"""
from CantusFirmusProducer import CFProducer
from FirstSpeciesCP import FSProducer
import json
from music21 import *
import random


N = 1000 #number of cf to find all fs on
LENGTH = 9 #length of cf (and therefore fs)


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
#cantus firmus
CFcomposer = CFProducer(every_possible_interval,MajorIntervalsFull)

CFcomposer.produceCF(LENGTH,"C4",verbose=False)

#first species
FScomposer = FSProducer(every_possible_interval,MajorIntervalsFull)
#read all data in
with open("generated_melodies.txt") as f:
    content = f.read()
#split content by \n
content = set(content.split(","))
for i in range(N):
    #get a random line from content and remove it
    line = random.choice(tuple(content))
    content.remove(line)
    cfdict = json.loads(line.strip())

    #convert cf dict melody to list of music21 notes
    cf = melodyToNotes(cfdict["melody"])
    #print(cf)
    FScomposer.reset()
    FScomposer.produceFS(cf,verbose=False)
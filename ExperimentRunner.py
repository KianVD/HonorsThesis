"""run this program to generate all first species counterpoints on all cantus firmuses of 
specified length, just change the length"""
from CantusFirmusProducer import CFProducer
from FirstSpeciesCP import FSProducer
import json
from music21 import *
from wakepy import keep

LENGTH = 8

def melodyToMidi(melody):
    melodyNotes = melody.split(",")
    returnMidi = []
    for notename in melodyNotes:
        returnMidi.append(note.Note(notename).pitch.midi)
    return returnMidi

print(f"Collecting data for all cantus firmus of length {LENGTH}")

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
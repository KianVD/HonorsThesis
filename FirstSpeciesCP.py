"""Class to produce all possible first species counterpoints on a given cantus firmus
Inherits from CFProducer"""
from music21 import *
import numpy as np
from graphviz import Digraph
from TreeNode import TreeNode
from CantusFirmusProducer import CFProducer 
import random
import json
import os
from pathlib import Path

#use classes to build a tree with all the possibilities, then follow random to choose one fscp


class FSProducer(CFProducer):
    def __init__(self,epi,Mintervals):
        self.every_possible_interval = epi
        self.major_intervals = Mintervals
        self.cflen =0
        self.root = None
        self.tree = None
        self.leaves = []
        self.tonic = None #music21 note

    def reset(self):
        """resets all variables to avoid leakage across different runs with same fsproducer instance"""
        self.cflen = 0
        self.root = None
        self.tree = None
        self.leaves = []
        self.tonic = None

    def produceFS(self,cf, verbose =False):
        """given the cantus firmus, produce a first species counterpoint melody that lines up with 
        counterpoint rules and print both melodies 

        for now assume quarterLength is always 1 when creating notes (default)
        
        @params
        list cf a list of music21 notes corresponding to the cantus firmus"""

        if verbose:
            print(cf)
            print("\nlength: ",len(cf),"\n")
        #create streams for cantus firmus and first species
        cfstream = stream.Part(cf)
        fsstream = stream.Part()
        #start with blank node (because there are multiple possible starting notes (1  3 and 5))
        self.root = TreeNode("N/A",False)
        #get length of cf 
        cflen = len(cf)
        self.cflen =cflen
        self.tonic = cf[0]
        #insert dummy at start of cf for generating tree
        cf.insert(0,"N/A")
        #create tree
        self.generateFSTree(self.root,cflen,cf,0,self.tonic,1,"N/A","N/A",False) 
        #create and render tree viz
        if verbose:
            self.tree = self.build_graphviz_tree(self.root)
            self.tree.render("tree", format="png", view=True)

        
        if verbose:
            
            #traverse tree and add get random valid path
            fs = self.traverseTreeDFS(self.root,True)
            #add fs to fsstream
            for nnote in fs:
                fsstream.append(nnote)
            #create full stream
            fullpiece = stream.Stream()
            #insert first species stream
            fullpiece.insert(0,fsstream)
            #insert cantus firmus stream
            fullpiece.insert(0,cfstream)
            fullpiece.show()
        #make sure to already have a results folder
        #if not os.path.isdir("results"):
            #Path("results").mkdir(exist_ok=True)
        self.writeData("results/" + self.convertCFtoFilename(cf[1:]))

    def generateFSTree(self,parent, nodesLeft,cf,dirJumped,currClimax,climaxCount,lowestNote,highestNote,tieUsed):
        """generate all possible first species to accompany given cantus firmus, abandoning paths as they fail.
        final, correct paths will have a value of True as their accepting parameter, indicating the path to get 
        to that node was a valid counterpoint
        
        @params
        parent parent of currnode
        nodesLeft how many nodes until first species is finished
        cf original cantus firmus
        dirJumped
        currClimax music21 note
        climaxCount
        lowestNote
        highestNote
        tieUsed bool"""
        #find possible notes 
        possibleNotes = self.getPossibleNotes(parent.nodenote,cf[-(nodesLeft+1)],cf[-nodesLeft],dirJumped,cf[1].transpose("P8"),True,nodesLeft,lowestNote,highestNote,tieUsed)
        #add each note onto tree as node
        for n in possibleNotes:
            #get these climax variables for each possible note
            nClimax, nClimaxCount = self.getNewClimax(n,currClimax,climaxCount)

            if nodesLeft <= 1: #base case, final note
                if nClimaxCount > 1: 
                    continue #skip making an accepting node if it will duplicate the climax

                newNode = TreeNode(n,True)
                parent.children.append(newNode)
                newNode.parent = parent
                newNode.tieUsed = tieUsed
                newNode.leapCount = parent.leapCount #update leapcount
                self.leaves.append(newNode)
            else: #continue tree at next step
                newNode = TreeNode(n,False)
                newNode.parent = parent
                parent.children.append(newNode)
                #calculate if the chosen note n is more than a third, and update dirJumped accordingly
                nextDirJumped = self.getNextDirJumped(parent,n,dirJumped)

                if abs(nextDirJumped) == 1:
                    newNode.leapCount = parent.leapCount + 1
                else:
                    newNode.leapCount = parent.leapCount

                newLowestNote,newHighestNote = self.computeNewExtremes(lowestNote,highestNote,n)

                #ensureCadence stops last note from being a tie
                if n == parent.nodenote:
                    tieUsed = True

                self.generateFSTree(newNode,nodesLeft-1,cf,nextDirJumped,nClimax,nClimaxCount,newLowestNote,newHighestNote,tieUsed)
        
    def EnsureOppositeCadence(self,weights,currentFSnote, transtonic,nodesLeft,nextCFnote):
        """ensures that the first species counterpoint has the opposite cadence from the cantus firmus"""
        if nodesLeft == 2:
            acceptableIntervals = []
            cadenceBeginnings = []
            possibleIntervals = []
            #if there are two notes left, and nextcfnote is 2nd degree we need 7th for fs
            #and vice versa
            #find if nextCFnote is second degrre or seventh
            sc = scale.MajorScale(transtonic)
            scaleDegree = sc.getScaleDegreeFromPitch(nextCFnote)
            if scaleDegree == 2:
                #cf cadence is 2nd degree to tonic
                cadenceBeginnings =[transtonic.transpose("-m2"),transtonic.transpose("M7"),transtonic.transpose("-m9")]
                for cbnote in cadenceBeginnings:
                    acceptableIntervals.append(interval.Interval(currentFSnote,cbnote))
                for itvl in acceptableIntervals:
                    if abs(itvl.semitones) <= 12 and abs(itvl.semitones) >= -12: #to prevent leaps greater than 12 semitones (not possible in current framework)
                        possibleIntervals.append(itvl.semitones+12)
            elif scaleDegree == 7:
                #cf cadence is 7th degree to tonic
                cadenceBeginnings = [transtonic.transpose("M2"),transtonic.transpose("M9"),transtonic.transpose("-m7")]
                for cbnote in cadenceBeginnings:
                    acceptableIntervals.append(interval.Interval(currentFSnote,cbnote))
                for itvl in acceptableIntervals:
                    if abs(itvl.semitones) <= 12 and abs(itvl.semitones) >= -12: #to prevent leaps greater than 12 semitones (not possible in current framework)
                        possibleIntervals.append(itvl.semitones+12)
            else:
                print("There is no cadence in cantus firmus")

            return weights @ self.partialIdentityMatrix(possibleIntervals)

        
        return weights
    
    def AvoidParallelPerfectConsonance(self,weights,currentCFnote,nextCFnote, currentFSnote):

        verticalinterval = interval.Interval(currentCFnote,currentFSnote)

        #if interval between current cf and fs is perfect
        if((abs(verticalinterval.semitones)%12) in [7,0]):
            #then find interval from current cf to next cf
            horintervalcf = interval.Interval(currentCFnote,nextCFnote)

            #this interval is not allowed
            return weights @ self.partialIdentityMatrixDelete([horintervalcf.semitones+12])
        else:

            return weights
        
    def AvoidSameConsecutivePerfect(self,weights,currentCFnote,nextCFnote,currentFSnote):

        verticalinterval = interval.Interval(currentCFnote,currentFSnote)
        currentperfect = (abs(verticalinterval.semitones)%12)
        if(currentperfect in [7,0]):
            #loop through each weight thats not already 0
            for i in range(len(weights)):
                if weights[i] != 0: #theres no point calculating it on stuff thats already 0
                    nextFSnote = currentFSnote.transpose(self.every_possible_interval[i])
                    nextvertinterval = interval.Interval(nextCFnote,nextFSnote)
                    if (abs(nextvertinterval.semitones)%12) == currentperfect:
                        weights[i] = 0 #=0, *= 0,  weights @ self.partialIdentityMatrixDelete([i]) all do same thing
        return weights



    def AvoidDirectPerfectIntervals(self,weights,currentCFnote,nextCFnote, currentFSnote):

        #for every possible next fs interval, 
        for i in range(len(weights)):
            if weights[i] != 0: #theres no point calculating it on stuff thats already 0
                #if the fs interval is not by step
                if(i not in [8,9,10,11,13,14,15,16]):
                    #and if the vertical interval between that resulting note and next cfnote is perfect,
                    vertinterval = interval.Interval(nextCFnote, currentFSnote.transpose(self.every_possible_interval[i]))
                    if ((abs(vertinterval.semitones)%12) in [7,0]):
                        #and if the interval is similar to cf interval
                        #cf interval polarity
                        cfinterval = interval.Interval(currentCFnote,nextCFnote).semitones
                        cfintervalpolarity = cfinterval/abs(cfinterval)
                        #fs interval polarity
                        fsintervalpolarity = 0
                        if self.every_possible_interval[i][0] == "-":
                            fsintervalpolarity = -1
                        else:
                            fsintervalpolarity = 1
                        if (fsintervalpolarity == cfintervalpolarity):
                            #then delete it
                            weights = weights @ self.partialIdentityMatrixDelete([i]) #i is already in terms of every possible interval (no need to add 12)
        return weights
    
    def NoSimultaneousLeaps(self,weights,currentCFnote,nextCFnote):

        cfinterval = interval.Interval(currentCFnote,nextCFnote)
        if(abs(cfinterval.semitones) > 4):
            return weights @ self.partialIdentityMatrix([8,9,10,11,12,13,14,15,16])
        return weights
    
    def LimitToConsonantVertical(self,weights,currentFSnote,nextCFnote):
        """limits to consonant vertical intervals between cf and fs
        
        @param weights
        """
        #for each interval, calculate the note you would end up at from current fs note


        for i in range(len(weights)):
            if weights[i] != 0: #theres no point calculating it on stuff thats already 0
                associatedInterval = self.every_possible_interval[i]
                newnote = currentFSnote.transpose(associatedInterval)

                # then calculate if the interval between nextcfnote and that note is consonant
                newInterval = interval.Interval(nextCFnote,newnote)
                
                if (abs(newInterval.semitones) % 12) not in [3,4,7,8,9,0]:
                    weights[i] *= 0
        return weights
    
    def NoOverlap(self,weights,nextCFnote,currentFSnote,nodesLeft):
        """ensures no overlap between cantus firmus and fs"""
        if not nodesLeft == 1:#allows last note to overlap
            for i in range(len(weights)):
                if weights[i] != 0: #theres no point calculating it on stuff thats already 0
                    associatedInterval = self.every_possible_interval[i]
                    newnote = currentFSnote.transpose(associatedInterval)

                    #if the new note is equal to or lower than cf note, then disqualify it
                    if (newnote.pitch <= nextCFnote.pitch):
                        weights[i] *= 0
        return weights
        

    def getPossibleNotes(self,currentFSnote,currentCFnote,nextCFnote,dirJumped,transtonic,major,nodesLeft,lowestNote,highestNote,tieUsed):
        """returns all possible notes by eliminating intervals from currentFSnote
        
        @params
        currentFSnote string representation of current fsnote (or "N/A")
        currentCFnote music 21 note (or "N/A")
        nextCFnote music 21 note (or "N/A")
        dirJumped indicates direction jumped last interval in fs (>0 means up, <0 means down, 0 means step)
        transtonic the transtonic of the scale, as music21 note, trasposed up an octave
        major whether the cantus firmus in the major scale or not (bool)
        nodesLeft how many nodes/notes are left in the song
        lowestNote: lowest music21 note in melody so far
        highestNote: highest music21 note in melody so far
        tieUsed: whether a tie has been used in the melody yet
        
        @return 
        list of possible notes (music 21 notes)
        """

        #check first case
        if(currentFSnote == "N/A"): #if no notes have been laid yet, possible notes are transtonic, third, and fifth
            return [transtonic,transtonic.transpose("M3"),transtonic.transpose("P5")] #this is all up an octave( keeps distance from cf to maximize produced fs while not duplicating melodies by having both transposed triads)
            #return [transtonic,transtonic.transpose("-P8"),transtonic.transpose("-m6"),transtonic.transpose("-P4")] #does tonic triad + octave

        weights=[1]*len(self.every_possible_interval)


        #good melody filters (CF)
        #1) limit to key
        if (major):
            #limit intervals to intervals in scale
            weights = self.LimitToMajorScale(weights,transtonic,currentFSnote) 
        else:
            pass #TODO
        #2) limit to range
        weights = self.LimitToRangeDynamic(weights,currentFSnote,lowestNote,highestNote)
        #3) step back after leap 
        if (dirJumped > 0): 
            possibleStepsAfterLeapUp = [10,11]#stepwise down #TWOS ONLY
            #if dirJumped is 1, only allow step down, if dirJumped is 2 allow step down or 3rd up (minor or major depending on scale degree), same for dirJumped 3
            if dirJumped > 1:
                #find scale degree to decide between minor or major required to stay in key
                possibleStepsAfterLeapUp.extend([15,16]) #add both minor and major, limitToKey already handles eliminating the wrong one(if its already 0, itll stay 0)
            #get new weights filtred for step backs
            weights = weights @ self.partialIdentityMatrix(possibleStepsAfterLeapUp)
        elif (dirJumped < 0):
            possibleStepsAfterLeapDown = [13,14]#stepwise up #ONLY TWOS

            if dirJumped < -1:
                #find scale degree to decide between minor or major required to stay in key
                possibleStepsAfterLeapDown.extend([8,9])
            #get new weights
            weights = weights @ self.partialIdentityMatrix(possibleStepsAfterLeapDown)
        #4) end in cadence
        weights = self.EnsureCadence(weights,currentFSnote,transtonic,nodesLeft)
        
        #DO NOT have to resolve leading tone for first species-- weights = self.ResolveLeadingTone(weights,transtonic,currentFSnote)

        #first species exclusive filters
        #1) only consonant vertical intervals NO second, fourth, seventh, aug, dim, tritone
        weights = self.LimitToConsonantVertical(weights,currentFSnote,nextCFnote)
        #2) no parallel perfect consonances
        weights = self.AvoidParallelPerfectConsonance(weights,currentCFnote,nextCFnote,currentFSnote)
        #2.5) no contrary perfect intervals (accomplished by avoid same consecutive perfect interval)
        weights = self.AvoidSameConsecutivePerfect(weights,currentCFnote,nextCFnote,currentFSnote)
        #3) no direct perfect intervals
        weights = self.AvoidDirectPerfectIntervals(weights,currentCFnote,nextCFnote,currentFSnote)
        #4) no simultaneous leaps
        weights = self.NoSimultaneousLeaps(weights,currentCFnote,nextCFnote)
        #4.5) voices may not overlap or cross
        weights = self.NoOverlap(weights,nextCFnote,currentFSnote,nodesLeft)
        #5)end on opposite cadence
        weights = self.EnsureOppositeCadence(weights,currentFSnote,transtonic,nodesLeft,nextCFnote)
        #once all filters have been applied------------------
        #6) disallow tied note if tie has been used
        if tieUsed:
            weights = weights @ self.partialIdentityMatrixDelete([12])#12 is middle, P1

        possibleNotes = []
        for i in range(len(weights)):
            if weights[i] != 0:
                associatedInterval = self.every_possible_interval[i]
                possibleNotes.append(currentFSnote.transpose(associatedInterval))

        return possibleNotes

    def traverseTreeDFS(self,root,randomPush=False):
        """
        traverses the built tree and choose a depth first path off the tree to return as list of notes

        @params
        root node to traverse from
        randomPush if true, adds new nodes to the stack in a random order, to choose a path at random on the tree, otherwise, chooses first node everytime
        
        @return
        list of notes (music21 notes)"""

        #traverse tree starting at root and return list of notes with stack
        currnode = root
        stack = []
        path = [0]*self.cflen #dont add first node to path, that is dummy node
        level = -1 #uses level to set correct note in path, when iterating throuhg
        while currnode.accept == False:#there will be an error here : popping from empty stack if no melody works
            #put all children of node in list
            children = currnode.children[:]
            #scramble order
            if randomPush:
                random.shuffle(children)

            #add children
            for child in children:
                stack.append((child,level+1))
            #pop first out 
            if not stack:#if stack is empty
                raise Exception("There is no possible first species counter point for this cantus firmus")

            currnode,level = stack.pop()
            path[level] = currnode.nodenote #set the index level to the new note, rather than appending
        

        return path
    
    def convertCFtoFilename(self,cf):
        return "_".join(note.nameWithOctave for note in cf)

    def writeData(self,filename):
        sc = scale.MajorScale(self.tonic)
        #print(f"There are {len(self.leaves)} possible first species counterpoins for given cantus firmus")
        with open(filename,"w") as f:
            for leafNode in self.leaves:
                notes = [leafNode.nodenote.nameWithOctave]
                currnode = leafNode
                for _ in range(self.cflen-1):
                    currnode = currnode.parent
                    notes.append(currnode.nodenote.nameWithOctave)

                #find starting note scale degree
                scaleDegree = sc.getScaleDegreeFromPitch(note.Note(notes[-1]))
                
                writeDict = {
                    "melody": ",".join(reversed(notes)),
                    "leapCount": leafNode.leapCount,
                    "tieUsed" : leafNode.tieUsed,
                    "startingNote": scaleDegree
                }
                f.write(json.dumps(writeDict) + "\n")


def main():
    # we will be given a list of notes representing the cantus firmus
    #cf = produceCF(7,7,1,"C4")

    #every possible interval within an octave from a note
    every_possible_interval = ["-P8", "-M7","-m7","-M6","-m6","-P5","-D5","-P4","-M3","-m3","-M2","-m2","P1","m2","M2","m3","M3","P4","D5","P5","m6","M6","m7","M7","P8"]#12 is middle
    #possible intervals from each scale degree in a major scale  + P1 for ties
    MajorIntervalsFull = {1:["M2","M3","P4","P5","M6","P8","-m2","-m3","-P4","-P5","-m6","-P8","P1"],
                      2:["M2","m3","P4","P5","P8","-M2","-m3","-P4","-P5","-M6","-P8","P1"],
                      3:["m2","m3","P4","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8","P1"],
                      4:["M2","M3","P5","M6","P8","-m2","-m3","-P4","-m6","-P8","P1"],
                      5:["M2","M3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-m6","-P8","P1"],
                      6:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8","P1"],
                      7:["m2","m3","P4","m6","P8","-M2","-M3","-P5","-M6","P1"] 
                      }

    FScomposer = FSProducer(every_possible_interval,MajorIntervalsFull)


    cf1 = [note.Note("F4"),note.Note("G4"),note.Note("A4"),note.Note("F4"),note.Note("D4"),note.Note("E4"),note.Note("F4"),note.Note("C5"),note.Note("A4"),note.Note("F4"),note.Note("G4"),note.Note("F4")]
    cf2 = [note.Note("C4"),note.Note("D4"),note.Note("E4"),note.Note("F4"),note.Note("D4"),note.Note("C4")]
    cf3 = [note.Note("C4"),note.Note("E4"),note.Note("B3"),note.Note("C4"),note.Note("G3"),note.Note("D4"),note.Note("C4")]
    cf4 = [note.Note("C4"),note.Note("D4"),note.Note("E4"),note.Note("D4"),note.Note("C4")]
    cf5 = [note.Note("C4"),note.Note("D4"),note.Note("E4"),note.Note("A4"),note.Note("G4"),note.Note("F4"),note.Note("E4"),note.Note("D4"),note.Note("C4")] #cf with possible oblique motion in fs
    cf6 = [note.Note("C4"),note.Note("C3"),note.Note("D3"),note.Note("A3"),note.Note("G3"),note.Note("E4"),note.Note("D4"),note.Note("C4")] 
    cf7 = [note.Note("C4"),note.Note("D4"),note.Note("D5"),note.Note("C5")] #impossible oned
    cf8 = [note.Note("C4"),note.Note("F4"),note.Note("D4"),note.Note("A4"),note.Note("G4"),note.Note("D5"),note.Note("B4"),note.Note("C5")] #impossible one?
    cf9 = [note.Note("C4"),note.Note("G4"),note.Note("F4"),note.Note("G4"),note.Note("C5"),note.Note("A4"),note.Note("D5"),note.Note("C5")]

    FScomposer.produceFS(cf9,verbose=True)
    #print(FScomposer.getPossibleNotes(note.Note("B4"),note.Note("G4"),note.Note("F4"),0,note.Note("C4"),True,4,note.Note("B4"),note.Note("F5"),False)) #in these specific rules, we make 7th scale degree always resolve to tonic


if __name__ == "__main__":
    main()
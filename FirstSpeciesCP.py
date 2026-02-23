"""start thinking about how go about this"""
from CFWithFilters import *
from music21 import *
import numpy as np
from graphviz import Digraph

#TODO put all functions in the FSProducer class so it can call from self rather than using global var

#use classes to build a tree with all the possibilities, then follow random to choose one fscp
class TreeNode():
    def __init__ (self,nodenote,accept):
        self.nodenote = nodenote
        self.children = []
        self.accept = accept


class FSProducer():
    def __init__(self,epi):
        self.every_possible_interval = epi
        self.cflen =0

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
        root = TreeNode("N/A",False)
        #get length of cf 
        cflen = len(cf)
        self.cflen =cflen
        #insert dummy at start of cf for generating tree
        cf.insert(0,"N/A")
        #create tree
        self.generateFSTree(root,cflen,cf,0)
        #create and render tree viz
        tree = self.build_graphviz_tree(root)
        tree.render("tree", format="png", view=True)
        #traverse tree and add get random valid path
        fs = self.traverseTreeDFS(root,True)
        #add fs to fsstream
        for nnote in fs:
            fsstream.append(nnote)
        
        #create full stream
        fullpiece = stream.Stream()
        #insert first species stream
        fullpiece.insert(0,fsstream)
        #insert cantus firmus stream
        fullpiece.insert(0,cfstream)
        if verbose:
            fullpiece.show()

    def generateFSTree(self,parent, nodesLeft,cf,dirJumped):
        """generate all possible first species to accompany given cantus firmus, abandoning paths as they fail.
        final, correct paths will have a value of True as their accepting parameter, indicating the path to get 
        to that node was a valid counterpoint
        
        @params
        parent parent of currnode
        nodesLeft how many nodes until first species is finished
        cf original cantus firmus"""
        #find possible notes #TODO return weights instead of notes and convert to ntoes out here, to make finding dirJumped easier
        possibleNotes = self.getPossibleNotes(parent.nodenote,cf[-(nodesLeft+1)],cf[-nodesLeft],dirJumped,cf[1].transpose("P8"),True,nodesLeft)#TODO allow for minor
        #add each note onto tree as node
        for n in possibleNotes:
            if nodesLeft <= 1: #base case, final note
                newNode = TreeNode(n,True)
                parent.children.append(newNode)
            else: #continue tree at next step
                newNode = TreeNode(n,False)
                parent.children.append(newNode)
                #calculate if the chosen note n is more than a third, and update dirJumped accordingly
                nextDirJumped = 0
                sm = 0
                if parent.nodenote != "N/A":
                    sm = interval.Interval(parent.nodenote, n).semitones #make sure the first note is on the left here
                    if sm > 4:
                        nextDirJumped = 1
                    elif sm < -4:
                        nextDirJumped = -1
                self.generateFSTree(newNode,nodesLeft-1,cf,nextDirJumped)

    def partialIdentityMatrix(self,preserved_indeces):
        """creates an identity matrix of size of every possible interval,
        with only the specified diagonals remaining
        
        @param preserved_indices indices to keep"""
        matrixWidth = len(self.every_possible_interval)
        newMatrix = np.zeros((matrixWidth,matrixWidth),dtype =int)
        for i in preserved_indeces:
            newMatrix[i,i] = 1
        return newMatrix
    def partialIdentityMatrixDelete(self,deleted_indices):
        """creates an identity matrix of size of every possible interval,
        with only the specified diagonals as 0
        
        @param preserved_indices indices to delete"""
        matrixWidth = len(self.every_possible_interval)
        newMatrix = np.zeros((matrixWidth,matrixWidth),dtype =int)
        for i in range(len(self.every_possible_interval)):
            if i not in deleted_indices:
                newMatrix[i,i] = 1
        return newMatrix
    
    def EnsureCadence(self,weights,currentFSnote,transtonic,nodesLeft):
        """ensures the  cadence happens
        
        @param weights
        nodesleft
        """
        possibleIntervals = []
        acceptableIntervals = []
        # allow it to end on cf tonic transposed up 1 octave or 2 octaves

        if nodesLeft == 2:
            # find intervals from currentfsnote to 2 semitones above transtonic and 1 semitone below (scale degree 2 and scale degree 7 major) 
            # regardless of minor or major scale, these are the only two notes for cadence
            #multiply those times 1, else by 0
            cadenceBeginnings = [transtonic.transpose("M2"),transtonic.transpose("M9"),transtonic.transpose("-m2"),transtonic.transpose("M7")]

            
            #get intervals from current note to 4 possible notes right before tonic (transtonic and transtonic transposed 1 octave higher)
            for cbnote in cadenceBeginnings:
                acceptableIntervals.append(interval.Interval(currentFSnote,cbnote))

            for itvl in acceptableIntervals:
                if abs(itvl.semitones) <= 12 and abs(itvl.semitones) >= -12: #to prevent leaps greater than 12 semitones (not possible in current framework)
                    possibleIntervals.append(itvl.semitones+12)
            return weights @ self.partialIdentityMatrix(possibleIntervals)
            


        elif nodesLeft == 1:
            #find interval from currentfsnote to transtonic 
            #multilply that times 1 else by 0
            acceptableIntervals = [interval.Interval(currentFSnote,transtonic),interval.Interval(currentFSnote,transtonic.transpose("P8"))]
            for itvl in acceptableIntervals:
                if abs(itvl.semitones) <= 12 and abs(itvl.semitones) >= -12: #to prevent leaps greater than 12 semitones (not possible in current framework)
                    possibleIntervals.append(itvl.semitones+12)
            return weights @ self.partialIdentityMatrix(possibleIntervals)

        else:
            return weights
        
    def EnsureOppositeCadence(self,weights,currentFSnote, transtonic,nodesLeft,nextCFnote):
        """ensures that the first species counterpoint has the opposite cadence from the cantus firmus"""
        if nodesLeft == 2:
            acceptableIntervals = []
            cadenceBeginnings = []
            possibleIntervals = []
            #if there are two notes left, and nextcfnote is 2nd degree we need 7th for fs
            #and vice versa
            interval1 = interval.Interval(nextCFnote,transtonic.transpose("-P8")) #next CFnote should be second to last #this is getting cf tonic
            if interval1.semitones < 0:
                #cf cadence is 2nd degree to tonic
                cadenceBeginnings =[transtonic.transpose("-m2"),transtonic.transpose("M7")]
                for cbnote in cadenceBeginnings:
                    acceptableIntervals.append(interval.Interval(currentFSnote,cbnote))
                for itvl in acceptableIntervals:
                    if abs(itvl.semitones) <= 12 and abs(itvl.semitones) >= -12: #to prevent leaps greater than 12 semitones (not possible in current framework)
                        possibleIntervals.append(itvl.semitones+12)
            elif interval1.semitones > 0:
                #cf cadence is 7th degree to tonic
                cadenceBeginnings = [transtonic.transpose("M2"),transtonic.transpose("M9")]
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
    
    def NoOverlap(self,weights,nextCFnote,currentFSnote):
        """ensures no overlap between cantus firmus and fs"""
        for i in range(len(weights)):
            if weights[i] != 0: #theres no point calculating it on stuff thats already 0
                associatedInterval = self.every_possible_interval[i]
                newnote = currentFSnote.transpose(associatedInterval)

                #if the new note is equal to or lower than cf note, then disqualify it
                if (newnote.pitch <= nextCFnote.pitch):
                    weights[i] *= 0
        return weights

    def getPossibleNotes(self,currentFSnote,currentCFnote,nextCFnote,dirJumped,transtonic,major,nodesLeft):
        """returns all possible notes by eliminating intervals from currentFSnote
        
        @params
        currentFSnote string representation of current fsnote (or "N/A")
        currentCFnote music 21 note (or "N/A")
        nextCFnote music 21 note (or "N/A")
        dirJumped indicates direction jumped last interval in fs (>0 means up, <0 means down, 0 means step)
        transtonic the transtonic of the scale, as music21 note, trasposed up an octave
        major whether the cantus firmus in the major scale or not (bool)
        nodesLeft how many nodes/notes are left in the song
        
        @return 
        list of possible notes (music 21 notes)
        """

        #check first case
        if(currentFSnote == "N/A"): #if no notes have been laid yet, possible notes are transtonic, third, and fifth
            return [transtonic,transtonic.transpose("M3"),transtonic.transpose("P5")]

        weights=[1]*len(self.every_possible_interval)


        #good melody filters (CF)
        #1) limit to key
        if (major):
            #limit intervals to intervals in scale
            weights = LimitToMajorScale(weights,transtonic,currentFSnote) 
        else:
            pass #TODO
        #2) limit to range
        weights = LimitToRange(weights,transtonic.nameWithOctave,currentFSnote)#TODO make it so all these functions accept music21 notes note strings
        #3) step back after leap 
        if (dirJumped > 0):
            weights = weights @ self.partialIdentityMatrix([8,9,10,11])#stepwise down
        elif (dirJumped < 0):
            weights = weights @ self.partialIdentityMatrix([13,14,15,16])#stepwise up
        #4) end in cadence
        weights = self.EnsureCadence(weights,currentFSnote,transtonic,nodesLeft)
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
        weights = self.NoOverlap(weights,nextCFnote,currentFSnote)
        #5)end on opposite cadence
        weights = self.EnsureOppositeCadence(weights,currentFSnote,transtonic,nodesLeft,nextCFnote)
        #once all filters have been applied------------------

        possibleNotes = []
        for i in range(len(weights)):
            if weights[i] != 0:
                associatedInterval = self.every_possible_interval[i]
                possibleNotes.append(currentFSnote.transpose(associatedInterval))

        return possibleNotes
    def build_graphviz_tree(self,root):
        dot = Digraph()

        def dfs(node):

            for child in node.children:
                if child.accept:
                    dot.node(str(id(child)), child.nodenote.nameWithOctave,color = 'green')
                else:
                    dot.node(str(id(child)), child.nodenote.nameWithOctave)
                dot.edge(str(id(node)), str(id(child)))
                dfs(child)

        dot.node(str(id(root)), "N/A")
        dfs(root)
        return dot

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
        while currnode.accept == False:#TODO there will be an error here : popping from empty stack if no melody works
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


def main():
    # we will be given a list of notes representing the cantus firmus
    #cf = produceCF(7,7,1,"C4")

    FScomposer = FSProducer(EVERY_POSSIBLE_INTERVAL)


    cf1 = [note.Note("F4"),note.Note("G4"),note.Note("A4"),note.Note("F4"),note.Note("D4"),note.Note("E4"),note.Note("F4"),note.Note("C5"),note.Note("A4"),note.Note("F4"),note.Note("G4"),note.Note("F4")]
    cf2 = [note.Note("C4"),note.Note("D4"),note.Note("E4"),note.Note("F4"),note.Note("D4"),note.Note("C4")]
    cf3 = [note.Note("C4"),note.Note("E4"),note.Note("B3"),note.Note("C4"),note.Note("G3"),note.Note("D4"),note.Note("C4")]

    FScomposer.produceFS(cf3,verbose=True)


if __name__ == "__main__":
    main()
"""a standalone class to produce tree of cantus firmus based on fux fixed rules
rules will all be methods of cfproducer class"""
from music21 import *
import numpy as np
from graphviz import Digraph
from TreeNode import TreeNode
import random
import json

class CFProducer():
    def __init__(self,epi,Mintervals):
        self.every_possible_interval = epi
        self.major_intervals = Mintervals
        self.n = 0
        self.root = None
        self.tree = None
        self.leaves = []

    def produceCF(self,n,tonic,filename="generated_melodies",verbose=False):
        """create and show cantus firmus
        return list of notes"""

        if verbose:
            print(f"generating all cantus firmus of length {n}")
        self.n = n

        #init start of tree
        self.root = TreeNode("N/A",False)

        self.generateTree(self.root,self.n,0,note.Note(tonic),note.Note(tonic),1,"N/A","N/A")

        #create and render tree viz
        self.tree = self.build_graphviz_tree(self.root)
        if verbose:
            self.tree.render("tree", format="png", view=True)

        cf = self.traverseTreeDFS(self.root,True)

        if verbose:
            cfstream = stream.Stream()
            for nnote in cf:
                cfstream.append(nnote)
            cfstream.show()
        self.writeData(f"{filename}.txt")

        return cf
    
    def getNewClimax(self,newNote,currClimax,climaxCount):
        #check if climax is duplicated for each note
        if newNote.pitch > currClimax.pitch:
            currClimax = newNote
            climaxCount = 1
        elif newNote.pitch == currClimax.pitch:
            climaxCount += 1

        return currClimax,climaxCount
    
    def getNextDirJumped(self,parent,nextNote,currDirJumped):
        """returns nextDirJumped for a given nextNote, ran on each possible note at each step
        
        dirJumped: the direction of a leap made to get to current note (accounts for arpeggios)
        dirJumped key is as follows:
        0 is no jump to next note
        1 is jump up besides p4
        -1 is jump down besides p4
        2 is perfect fourth up
        -2 is perfect fourth down
        3 is perfect fourth then a third up
        -3 is perfect fourth then a third down

        @param 
        parent: current note node
        nextNote: the next note of melody, music21 note
        currDirJumped: the dirJumped var for the note before current note to current note
        
        returns: nextDirJumped
        """
        nextDirJumped = 0
        sm = 0
        if parent.nodenote != "N/A":
            sm = interval.Interval(parent.nodenote, nextNote).semitones #make sure the first note is on the left here
            if sm > 4: #leap up
                nextDirJumped = 1
                if sm == 5:
                    nextDirJumped = 2 #2 signifies this jump is a perfect fourth up
            elif sm < -4: #leap down
                nextDirJumped = -1
                if sm == -5:
                    nextDirJumped = -2
            #new variable to keep track of arpeggios: we can assume there is only 1 4:3:3 pattern in an arpeggio at most 
            # due to octave and 3rd range, so we only need to keep track of if a 4th leap was made once (3rds arent leaps)
            #only valid 4th is perfect: 5 semitones
            if currDirJumped == 2 and sm in [3,4]: #if that last jump was a fourth and this move gonna be a 3rd in same direction (arpeggio)
                nextDirJumped = 3
            elif currDirJumped == -2 and sm in [-3,-4]: #down case
                nextDirJumped = -3
            elif currDirJumped == 3 and sm in [3,4]: #4:3:3 arpeggio has just transpired, need step down
                nextDirJumped = 1
            elif currDirJumped == -3 and sm in [-3,-4]: #down case (step up)
                nextDirJumped = -1

        return nextDirJumped

    def computeNewExtremes(self,lowestNote,highestNote,newNote):
        """compute extremes and give them back to generate tree to remember"""
        if lowestNote == "N/A" or highestNote == "N/A":
            lowestNote = newNote
            highestNote = newNote

        if lowestNote.pitch > newNote.pitch:
            lowestNote = newNote
        if highestNote.pitch < newNote.pitch:
            highestNote = newNote

        return lowestNote, highestNote

    def generateTree(self,parent,nodesLeft,dirJumped,tonic,currClimax,climaxCount,lowestNote,highestNote):
        """recursively generates tree of cantus firmuses
         
        @param parent node  
        nodesLeft
        dirJumped
        tonic 
        currClimax music21 note
        climaxCount
        lowestNote
        highestNote"""
        #find possible notes 
        possibleNotes = self.getPossibleNotes(parent.nodenote,dirJumped,tonic,True,nodesLeft,lowestNote,highestNote)
        #add each note onto tree as node

        for n in possibleNotes:
            #get these climax variables for each possible note
            nClimax, nClimaxCount = self.getNewClimax(n,currClimax,climaxCount)

            if nodesLeft <= 1: #base case, final note
                #check that the climax isn't duplicated
                if nClimaxCount > 1: 
                    continue #skip making an accepting node if it will duplicate the climax

                newNode = TreeNode(n,True)
                parent.children.append(newNode)
                newNode.parent = parent
                newNode.leapCount = parent.leapCount #update leapcount
                self.leaves.append(newNode)
            else: #continue tree at next step
                newNode = TreeNode(n,False)
                parent.children.append(newNode)
                newNode.parent = parent
                #calculate if the chosen note n is more than a third, and update dirJumped accordingly
                nextDirJumped = self.getNextDirJumped(parent,n,dirJumped)
                #update leap count in each node
                if abs(nextDirJumped) == 1:
                    newNode.leapCount = parent.leapCount + 1
                else:
                    newNode.leapCount = parent.leapCount
                #get the extremes for range calc
                newLowestNote,newHighestNote = self.computeNewExtremes(lowestNote,highestNote,n)
                
                self.generateTree(newNode,nodesLeft-1,nextDirJumped,tonic,nClimax,nClimaxCount,newLowestNote,newHighestNote)

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
    
    def EnsureCadence(self,weights,currentNote,tonic,nodesLeft):
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
            cadenceBeginnings = [tonic.transpose("M2"),tonic.transpose("-m2"),tonic.transpose("-m7"),tonic.transpose("M7"),tonic.transpose("M9"),tonic.transpose("-m9")] #any other 2 or 7 is out of range

            
            #get intervals from current note to 4 possible notes right before tonic (transtonic and transtonic transposed 1 octave higher)
            for cbnote in cadenceBeginnings:
                acceptableIntervals.append(interval.Interval(currentNote,cbnote))

            for itvl in acceptableIntervals:
                if abs(itvl.semitones) <= 12 and abs(itvl.semitones) >= -12: #to prevent leaps greater than 12 semitones (not possible in current framework)
                    possibleIntervals.append(itvl.semitones+12)
            return weights @ self.partialIdentityMatrix(possibleIntervals)
            


        elif nodesLeft == 1:
            #find interval from currentfsnote to transtonic 
            #multilply that times 1 else by 0
            acceptableIntervals = [interval.Interval(currentNote,tonic),interval.Interval(currentNote,tonic.transpose("P8")),interval.Interval(currentNote,tonic.transpose("-P8"))]
            for itvl in acceptableIntervals:
                if abs(itvl.semitones) <= 12 and abs(itvl.semitones) >= -12: #to prevent leaps greater than 12 semitones (not possible in current framework)
                    possibleIntervals.append(itvl.semitones+12)
            return weights @ self.partialIdentityMatrix(possibleIntervals)

        else:
            return weights
        
    def LimitToMajorScale(self,weights,tonic,currNote):
        """sets all intervals to 0 except for those in the given scale, depending on scaledegree
        
        @param prob the probability distribution we are working with 
        @param tonic tonic we are using music21note
        @param currNote the current note were on music21 note
        
        @return list of floats between 0 and 1, len 25"""
        #first figure out scale degree
        sc = scale.MajorScale(tonic)
        scaleDegree = sc.getScaleDegreeFromPitch(currNote)

        #use dictionary for scale
        AllowedIntervals = self.major_intervals[scaleDegree]

        for i in range(len(self.every_possible_interval)):
            weights[i] *= 1 if self.every_possible_interval[i] in AllowedIntervals else 0

        return weights
    
    def ResolveLeadingTone(self,weights,tonic,currNote):
        """if the current note is the leading tone, select only m2 as a possible interval
        
        @param weights the probability distribution we are working with 
        @param tonic tonic we are using music21 note
        @param currNote the current note were on music21 note
        
        @return weights"""
        sc = scale.MajorScale(tonic)
        scaleDegree = sc.getScaleDegreeFromPitch(currNote)

        if (scaleDegree == 7):
            return weights @ self.partialIdentityMatrix([13])
        else:
            return weights

    
    def LimitToRangeDynamic(self,weights,currNote,lowestNote,highestNote):
        """a new limit to range function that limits the entire interval of used notes to 1 and a 3rd, 
        updating the possible region based on 1.3 above lowest and 1.3 below highest
        
        @param weights weights
        @param tonic tonic (text)
        @param currNote current note (music21 note)
        @param lowestNote lowestNote in cf so far (music21 note )
        @param highestNote highestNote in cf so far (music21 note)
        
        @return new weights"""

        #compute the bounds and update weights as such---
        unallowedIntervals = []
        #find highest allowed note which is 1.3 above lowest note
        highestValidNote = lowestNote.transpose("M10") #M10 is octave plus major 3rd, max range for cf we decided on
        #find interval from currNote to highest allowed note
        currToHighItvl = interval.Interval(currNote,highestValidNote)
        #find that interval in epi
        if abs(currToHighItvl.semitones) <= 12 and abs(currToHighItvl.semitones) >= -12:
            epi_index = currToHighItvl.semitones+12
            #add anything above that interval to unallowed intervals
            unallowedIntervals.extend(self.every_possible_interval[:epi_index+1])#stop exclusive
        #now same for  lowest allowed note
        lowestValidNote = highestNote.transpose("-M10")

        currToLowItvl = interval.Interval(currNote,lowestValidNote)

        if abs(currToLowItvl.semitones) <= 12 and abs(currToLowItvl.semitones) >= -12:
            epi_index = currToLowItvl.semitones+12
            #add anything above that interval to unallowed intervals
            unallowedIntervals.extend(self.every_possible_interval[epi_index:]) #start inclusive

        return weights @ self.partialIdentityMatrixDelete(unallowedIntervals)

        


    def LimitToRange(self,weights,tonic,currNote):
        """make sure next intervals isnt too high or too low from start note
        For now ill just stop it from getting more than an octave from the tonic
        
        @param prob the prob dist
        @param tonic the originla tonic
        @param currNote the current note"""
        #make tonic into actual note type
        tonicNote = note.Note(tonic,quarterLength=1)

        #find interval from tonic to current note
        #tonicToCurr = interval.Interval(tonicNote, currNote)

        extremeNote = ""
        isLower = True
        if (currNote.pitch < tonicNote.pitch):
            #currNote is lower than tonic
            extremeNote = tonicNote.transpose("-P8")
            isLower = True
        else:
            #currNote is higher than tonic
            extremeNote = tonicNote.transpose("P8")
            isLower = False
        

        #find interval from currNote to most extreme note possible (this is what the next interval cant be higher than)
        currToExt = interval.Interval(currNote,extremeNote)
        currToExtName = currToExt.name
        if isLower:
            currToExtName = "-"+currToExtName
        #print(tonicNote.pitch,currNote.pitch,extremeNote.pitch, currToExtName)

        #find index of currtoext in everypossibleinterval
        if currToExtName =="-P1":
            currToExtName = "P1"
        extremeIndex = self.every_possible_interval.index(currToExtName)

        UnallowedIntervals = []

        if (isLower):
            #if currnote is lower than tonic, remove all intervals below
            #get subset of everypossibleinterval from start to extremeindex exclusive
            UnallowedIntervals.extend(self.every_possible_interval[:extremeIndex])
        else:
            #if currnote is higher than tonic, remove all intervals above
            #get subset of everypossibleinterval from extremeindex exclusive to end
            UnallowedIntervals.extend(self.every_possible_interval[extremeIndex+1:])


        for i in range(len(self.every_possible_interval)):
            #is the resulting note from this too far from tonic?
            weights[i] *= 0 if self.every_possible_interval[i] in UnallowedIntervals else 1

        return weights

    def getPossibleNotes(self,currentNote,dirJumped,tonic,major,nodesLeft,lowestNote,highestNote):
        """returns list of possible notes (music21 notes)
        
        params:
        currentNote: current music21 note of cantus firmus
        dirJumped: the direction of a leap made to get to current note (0 is no jump, 1 is jump up, -1 is jump down) 
            extended - (2 is perfect fourth up, -2 is perfect fourth down, 3 is perfect fourth then a third up, -3 is perfect fourth then a third down)
        tonic: music21 note of tonic
        major: boolean whether the cf is major or not
        nodesLeft: number of remaining notes in cf (1 is the lowest you can expect)
        lowestNote: lowest music21 note in melody so far
        highestNote: highest music21 note in melody so far
        
        returns:
        list of possible notes (music21 notes)
        """
        #check first case
        if(currentNote == "N/A"): #if no notes have been laid yet, possible notes are transtonic, third, and fifth
            return [tonic]
        
        weights=[1]*len(self.every_possible_interval)

        #good melody filters (CF)
        #1) limit to key
        if (major):
            #limit intervals to intervals in scale
            weights = self.LimitToMajorScale(weights,tonic,currentNote) 
        else:
            pass #TODO
        #2) limit to range
        weights = self.LimitToRangeDynamic(weights,currentNote,lowestNote,highestNote)
        #3) step back after leap 
        if (dirJumped > 0): 
            possibleStepsAfterLeapUp = [10,11]#stepwise down #ONLY TWOS
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
        weights = self.EnsureCadence(weights,currentNote,tonic,nodesLeft)
        #5) resolve leading tone always
        weights = self.ResolveLeadingTone(weights,tonic,currentNote)
        #disallow oblique motion no matter what in cantus firmus
        weights = weights @ self.partialIdentityMatrixDelete([12])#12 is middle, P1

        #convert interval weights to notes
        possibleNotes = []
        for i in range(len(weights)):
            if weights[i] != 0:
                associatedInterval = self.every_possible_interval[i]
                possibleNotes.append(currentNote.transpose(associatedInterval))
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
        path = [0]*self.n #dont add first node to path, that is dummy node
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
    
    def writeData(self,filename):
        print(f"There are {len(self.leaves)} possible cantus firmuses of length {self.n}")
        with open(filename,"w") as f:
            for leafNode in self.leaves:
                notes = [leafNode.nodenote.nameWithOctave]
                currnode = leafNode
                for _ in range(self.n-1):
                    currnode = currnode.parent
                    notes.append(currnode.nodenote.nameWithOctave)
                
                writeDict = {
                    "melody": ",".join(reversed(notes)),
                    "leapCount": leafNode.leapCount
                }
                f.write(json.dumps(writeDict) + "\n")
                
def main():
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
    
    CFcomposer = CFProducer(every_possible_interval,MajorIntervalsFull)

    cf = CFcomposer.produceCF(8,"C4",verbose=True)


if __name__ == "__main__":
    main()
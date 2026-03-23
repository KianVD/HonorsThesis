"""a standalone class to produce tree of cantus firmus based on fux fixed rules
rules will all be methods of cfproducer class"""
from music21 import *
import numpy as np
from graphviz import Digraph
from TreeNode import TreeNode
import random

class CFProducer():
    def __init__(self,epi,Mintervals):
        self.every_possible_interval = epi
        self.major_intervals = Mintervals
        self.n = 0
        self.root = None
        self.tree = None

    def produceCF(self,n,tonic,verbose=False):
        """create and show cantus firmus
        return list of notes"""

        if verbose:
            print(f"generating cantus firmus of length {n}")
        self.n = n

        #init start of tree
        self.root = TreeNode("N/A",False)

        self.generateTree(self.root,self.n,0,note.Note(tonic))

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

        return cf


    def generateTree(self,parent,nodesLeft,dirJumped,tonic):
        #find possible notes 
        possibleNotes = self.getPossibleNotes(parent.nodenote,dirJumped,tonic,True,nodesLeft)
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
                self.generateFSTree(newNode,nodesLeft-1,nextDirJumped)

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
        
    def LimitToMajorScale(self,weights,tonic,currNote):
        """sets all intervals to 0 except for those in the given scale, depending on scaledegree
        
        @param prob the probability distribution we are working with 
        @param tonic tonic we are using
        @param currNote the current note were on
        
        @return list of floats between 0 and 1, len 25"""
        #first figure out scale degree
        sc = scale.MajorScale(tonic)
        scaleDegree = sc.getScaleDegreeFromPitch(currNote)

        #use dictionary for scale
        AllowedIntervals = self.major_intervals[scaleDegree]

        for i in range(len(self.every_possible_interval)):
            weights[i] *= 1 if self.every_possible_interval[i] in AllowedIntervals else 0

        return weights

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

    def possibleNotes(self,currentNote,dirJumped,tonic,major,nodesLeft):
        #check first case
        if(currentNote == "N/A"): #if no notes have been laid yet, possible notes are transtonic, third, and fifth
            return tonic
        
        weights=[1]*len(self.every_possible_interval)

        #good melody filters (CF)
        #1) limit to key
        if (major):
            #limit intervals to intervals in scale
            weights = self.LimitToMajorScale(weights,tonic,currentNote) 
        else:
            pass #TODO
        #2) limit to range
        weights = self.LimitToRange(weights,tonic.nameWithOctave,currentNote)
        #3) step back after leap 
        if (dirJumped > 0):
            weights = weights @ self.partialIdentityMatrix([8,9,10,11])#stepwise down
        elif (dirJumped < 0):
            weights = weights @ self.partialIdentityMatrix([13,14,15,16])#stepwise up
        #4) end in cadence
        weights = self.EnsureCadence(weights,currentNote,tonic,nodesLeft)

        #TODO still need to add climax and arpeggio


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

def main():
    #every possible interval within an octave from a note
    every_possible_interval = ["-P8", "-M7","-m7","-M6","-m6","-P5","-D5","-P4","-M3","-m3","-M2","-m2","P1","m2","M2","m3","M3","P4","D5","P5","m6","M6","m7","M7","P8"]#12 is middle
    #possible intervals from each scale degree in a major scale 
    MajorIntervalsFull = {1:["M2","M3","P4","P5","M6","P8","-m2","-m3","-P4","-P5","-m6","-P8"],
                      2:["M2","m3","P4","P5","P8","-M2","-m3","-P4","-P5","-M6","-P8"],
                      3:["m2","m3","P4","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      4:["M2","M3","P5","M6","P8","-m2","-m3","-P4","-m6","-P8"],
                      5:["M2","M3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-m6","-P8"],
                      6:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      7:["m2"] #leading tone #TODO add everything back to this, and make a seperate function to enforce leading tone
                      }
    
    CFcomposer = CFProducer(every_possible_interval,MajorIntervalsFull)

    cf = CFcomposer.produceCF(8,"C4",verbose=True)


if __name__ == "__main__":
    main()
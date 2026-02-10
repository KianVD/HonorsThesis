"""start thinking about how go about this"""
from CFWithFilters import *
from music21 import *
import numpy as np

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
        possibleNotes = self.getPossibleNotes(parent.nodenote,cf[-(nodesLeft+1)],cf[-nodesLeft],dirJumped,cf[1].transpose("P8"),True)#TODO allow for minor
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
                if parent.nodenote != "N/A":
                    sm = interval.Interval(parent.nodenote, n).semitones #make sure the first note is on the left here
                    if sm > 4:
                        nextDirJumped = 1
                    elif sm < 4:
                        nextDirJumped = -1

                self.generateFSTree(newNode,nodesLeft-1,cf,nextDirJumped)

    def partialPreservingMatrix(self,preserved_indeces):
        matrixWidth = len(self.every_possible_interval)
        newMatrix = np.zeros((matrixWidth,matrixWidth),dtype =int)
        for i in preserved_indeces:
            newMatrix[i,i] = 1
        return newMatrix

    def getPossibleNotes(self,currentFSnote,currentCFnote,nextCFnote,dirJumped,tonic,major):
        """returns all possible notes by eliminating intervals from currentFSnote
        
        @params
        currentFSnote string representation of current fsnote (or "N/A")
        currentCFnote music 21 note (or "N/A")
        nextCFnote music 21 note (or "N/A")
        dirJumped indicates direction jumped last interval in fs (>0 means up, <0 means down, 0 means step)
        tonic the tonic of the scale, as music21 note
        major whether the cantus firmus in the major scale or not (bool)
        
        @return 
        list of possible notes (music 21 notes)
        """

        #check first case
        if(currentFSnote == "N/A"): #if no notes have been laid yet, possible notes are tonic, third, and fifth
            return [tonic,tonic.transpose("M3"),tonic.transpose("P5")]

        weights=[1]*len(self.every_possible_interval)


        #good melody filters (CF)
        #1) limit to key
        if (major):
            #limit intervals to intervals in scale
            weights = LimitToMajorScale(weights[:],tonic,currentFSnote)
        else:
            pass #TODO
        #2) limit to range
        weights = LimitToRange(weights[:],tonic.nameWithOctave,currentFSnote)#TODO make it so all these functions accept music21 notes note strings
        #3) step back after leap 
        if (dirJumped > 0):
            weights = weights @ self.partialPreservingMatrix([8,9,10,11])#stepwise down
        elif (dirJumped < 0):
            weights = weights @ self.partialPreservingMatrix([13,14,15,16])#stepwise up
        #4) end in cadence

        #first species exclusive filters
        #1) only consonant vertical intervals NO second, fourth, seventh, aug, dim

        #2) no parallel perfect consonances

        #3) no direct perfect intervals

        #4) no simultaneous leaps

        #5)end on opposite cadence

        #once all filters have been applied------------------

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
        list of notes (music21 notes)"""#TODO this function is wrong because if a path is wrong, the notes stay on the path list (may need recursive)

        #traverse tree starting at root and return list of notes with stack
        currnode = root
        stack = []
        path = [0]*self.cflen #dont add first node to path, that is dummy node
        level = -1
        while currnode.accept == False:
            #put all children of node in list
            if randomPush:
                #create a list of indices and scramble it
                ind = []
                for i in range(len(currnode.children)):
                    ind.append(i) 
                random.shuffle(ind)
                print(ind)
                #add children in new order
                for i in ind:
                    stack.append((currnode.children[i],level+1))

            else:
                for child in currnode.children:
                    stack.append((child,level+1))
            #pop first out 
            currnode,level = stack.pop()
            path[level] = currnode.nodenote
        

        return path


def main():
    # we will be given a list of notes representing the cantus firmus
    cf = produceCF(5,5,1,"C4")

    FScomposer = FSProducer(EVERY_POSSIBLE_INTERVAL)
    
    FScomposer.produceFS(cf,verbose=True)


if __name__ == "__main__":
    main()

#Required filters:
#0 same principles as cf?
#1 #Consonant vertical intervals only (1,3,5,6 only)
#2
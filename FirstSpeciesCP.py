"""start thinking about how go about this"""
from CFWithFilters import *
from music21 import *

#use classes to build a tree with all the possibilities, then follow random to choose one fscp
class TreeNode():
    def __init__ (self,nodenote,accept):
        self.nodenote = nodenote
        self.children = []
        self.accept = accept




def produceCPFS(cf, verbose =False):
    """given the cantus firmus, produce a first species counterpoint melody that lines up with 
    counterpoint rules and print both melodies 
    
    @params
    list cf a list of notes corresponding to the cantus firmus"""

    if verbose:
        print(cf)
    #create stream for cantus firmus
    cfstream = stream.Part(cf)
    #initialize same note length (first species)
    noteLength = cf[0].quarterLength
    #create stream for first species
    cpfsstream = stream.Part()
    #start with blank node (because there are multiple possible starting notes (1  3 and 5))
    root = TreeNode("N/A",False)
    #create tree
    goDownPath(root,len(cf),cf)
    #traverse tree and add get random valid path
    fs = traverseTree(root)
    #add fs to cpfsstream
    for nnote in fs:
        cpfsstream.append(nnote)
    
    #create full stream
    fullpiece = stream.Stream()
    #insert cantus firmus stream
    fullpiece.insert(0,cfstream)
    #insert first species stream
    fullpiece.insert(0,cpfsstream)
    fullpiece.show()

def goDownPath(parent, nodesLeft,cf):
    """explore a path recursively
    
    
    @params
    parent parent of currnode
    nodesLeft how many nodes until first species is finished
    cf original cantus firmus"""
    #base case
    if(nodesLeft == 1):
        #the tonic must be next
        newNode = TreeNode(cf[-1],True)
        parent.children.append(newNode)
        return
    else:
        #otherwise, if there are more nodes to go, decide based on weights
        possibleNotes = getPossibleNotes(parent.nodenote,cf[-nodesLeft])
        for nnote in possibleNotes:
            newNode = TreeNode(nnote,False)
            parent.children.append(newNode)
            return goDownPath(newNode,nodesLeft-1)


def getPossibleNotes(previousFSnote,nextCPnote):
    """
    
    @params
    
    @return 
    list of possible notes (music 21 notes)
    """

    return []

def traverseTree(root):
    """

    @params
    
    @return
    list of notes (music21 notes)"""
    return []


def main():
    # we will be given a list of notes representing the cantus firmus
    cf = produceCF(8,16,1,"C4")

    produceCPFS(cf,verbose=True)


if __name__ == "__main__":
    main()

#Required filters:
#0 same principles as cf?
#1 #Consonant vertical intervals only (1,3,5,6 only)
#2
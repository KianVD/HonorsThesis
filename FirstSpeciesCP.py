"""start thinking about how go about this"""
from CFWithFilters import *
from music21 import *

#use classes to build a tree with all the possibilities, then follow random to choose one fscp
class TreeNode():
    def __init__ (self,nodenote,accept):
        self.nodenote = nodenote
        self.children = []
        self.accept = accept




def produceFS(cf, verbose =False):
    """given the cantus firmus, produce a first species counterpoint melody that lines up with 
    counterpoint rules and print both melodies 

    for now assume quarterLength is always 1 when creating notes (default)
    
    @params
    list cf a list of music21 notes corresponding to the cantus firmus"""

    if verbose:
        print(cf)
    #create streams for cantus firmus and first species
    cfstream = stream.Part(cf)
    fsstream = stream.Part()
    #start with blank node (because there are multiple possible starting notes (1  3 and 5))
    root = TreeNode("N/A",False)
    #get length of cf 
    cflen = len(cf)
    #insert dummy at start of cf for generating tree
    cf.insert(0,"N/A")
    #create tree
    generateFSTree(root,cflen,cf,0)
    #traverse tree and add get random valid path
    fs = traverseTree(root)
    #add fs to fsstream
    for nnote in fs:
        fsstream.append(nnote)
    
    #create full stream
    fullpiece = stream.Stream()
    #insert cantus firmus stream
    fullpiece.insert(0,cfstream)
    #insert first species stream
    fullpiece.insert(0,fsstream)
    fullpiece.show()

def generateFSTree(parent, nodesLeft,cf,stepBackReq):
    """generate all possible first species to accompany given cantus firmus, abandoning paths as they fail.
    final, correct paths will have a value of True as their accepting parameter, indicating the path to get 
    to that node was a valid counterpoint
    
    @params
    parent parent of currnode
    nodesLeft how many nodes until first species is finished
    cf original cantus firmus"""
    #find possible notes
    possibleNotes = getPossibleNotes(parent.nodenote,cf[-(nodesLeft+1)],cf[-nodesLeft],stepBackReq)
    #add each note onto tree as node
    for n in possibleNotes:
        if nodesLeft <= 1: #base case, final note
            newNode = TreeNode(n,True)
            parent.children.append(newNode)
        else: #continue tree at next step
            newNode = TreeNode(n,False)
            parent.children.append(newNode)
            return generateFSTree(newNode,nodesLeft-1,cf,stepBackReq)


def getPossibleNotes(currentFSnote,currentCFnote,nextCFnote,dirJumped):
    """returns all possible notes
    
    @params
    currentFSnote string representation of current fsnote (or "N/A")
    currentCFnote music 21 note (or "N/A")
    nextCFnote music 21 note (or "N/A")
    dirJumped indicates direction jumped last interval in fs (>0 means up, <0 means down, 0 means step)
    
    @return 
    list of possible notes (music 21 notes)
    """


    return [note.Note("C4")]

def traverseTree(root):
    """
    traverses the built tree and choose a random path off the tree to return as list of notes

    @params
    
    @return
    list of notes (music21 notes)"""

    #traverse tree starting at root and return list of notes with stack
    currnode = root
    stack = []
    path = [] #dont add first node to path, that is dummy node
    while currnode.accept == False:
        #if there are no children and 
        #put all children of node in list
        for child in currnode.children:
            stack.append(child)
        #pop first out 
        currnode = stack.pop()
        path.append(currnode.nodenote)
    

    return path

def traverseTreeRecursive(currnode,path):
    #base case
    if currnode.accept == False and not currnode.children:
        return 
    elif currnode.accept == True and not currnode.children:
        return #a"ccepting:
    else:
        for child in currnode.children:
            path.append(child)
            currpath = traverseTreeRecursive(child,path) #stop here if you get to a node
            path.pop()


def main():
    # we will be given a list of notes representing the cantus firmus
    cf = produceCF(8,16,1,"C4")

    produceFS(cf,verbose=True)


if __name__ == "__main__":
    main()

#Required filters:
#0 same principles as cf?
#1 #Consonant vertical intervals only (1,3,5,6 only)
#2
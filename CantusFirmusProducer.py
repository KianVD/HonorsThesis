"""a standalone class to produce tree of cantus firmus based on fux fixed rules
rules will all be methods of cfproducer class"""
from CFWithFilters import *
from music21 import *
import numpy as np
from graphviz import Digraph
from TreeNode import TreeNode

class CFProducer():
    def __init__(self,epi):
        self.every_possible_interval = epi
        self.n = 0
        self.root = None
        self.tree = None

    def produceCF(self,n,verbose=False):
        """create and show cantus firmus
        return list of notes"""

        if verbose:
            print(f"generating cantus firmus of length {n}")
        self.n = n

        #init start of tree
        self.root = TreeNode("N/A",False)

        self.generateTree(self.root,self.n,0)

        #create and render tree viz
        self.tree = self.build_graphviz_tree(self.root)
        self.tree.render("tree", format="png", view=True)

        cf = self.traverseTreeDFS(self.root,True)

        if verbose:
            cfstream = stream.Stream()
            for nnote in cf:
                cfstream.append(nnote)
            cfstream.show()

        return cf


    def generateTree(self,parent,nodesLeft,dirJumepd):
        pass

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
    
    CFcomposer = CFProducer(every_possible_interval)

    cf = CFcomposer.produceCF(8,verbose=True)


if __name__ == "__main__":
    main()
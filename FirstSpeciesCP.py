"""start thinking about how go about this"""
from CFWithFilters import *
from music21 import *




def produceCPFS(cf, verbose =False):
    """given the cantus firmus, produce a first species counterpoint melody that lines up with 
    counterpoint rules and print both melodies 
    
    @params
    list cf a list of notes corresponding to the cantus firmus"""

    if verbose:
        print(cf)
    cfstream = stream.Part(cf)
    noteLength = cf[0].quarterLength
    cpfsstream = stream.Part()
    for cfnote in cf:
        #for each note TODO implement rules of counterpoint to add correct notes
        cpfsstream.append(note.Note("C4",quarterLength=noteLength))
    
    #figure out how to show two streams at once
    fullpiece = stream.Stream()
    fullpiece.insert(0,cfstream)
    fullpiece.insert(0,cpfsstream)
    fullpiece.show()



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
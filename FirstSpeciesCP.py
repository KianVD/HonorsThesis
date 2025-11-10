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
    for note in cf:
        #for each note
        pass



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
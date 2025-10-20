"""This tests out the idea of using individual functions to define a wieghted prob dist for  each rule"""

from music21 import *
import random


#global var
EveryPossibleInterval = ["-P8", "-M7","-m7","-M6","-m6","-P5","-D5","-P4","-M3","-m3","-M2","-m2","P1","m2","M2","m3","M3","P4","D5","P5","m6","M6","m7","M7","P8"]#12 is middle
#using D5 for tritone cuz idk (also len 25)
MajorIntervalsFull = {1:["M2","M3","P4","P5","M6","P8","-m2","-m3","-P4","-P5","-m6","-P8"],#take out p1 for one
                      2:["M2","m3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-M6","-P8"],
                      3:["m2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      4:["M2","M3","P5","M6","P8","-m2","-m3","-P4","-m6","-P8"], #P4 and -P5 not possible
                      5:["M2","M3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-m6","-P8"],
                      6:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      7:["m2"] #leading tone
                      }


#Here are the absolute rules (multiplying by 1 or 0) change this later

def LimitToMajorScale(prob,tonic,currNote):
    """sets all intervals to 0 except for those in the given scale, depending on scaledegree
    
    @param prob the probability distribution we are working with 
    @param tonic tonic we are using
    @param currNote the current note were on
    
    @return list of floats between 0 and 1, len 25"""
    #first figure out scale degree
    sc = scale.MajorScale(tonic)
    scaleDegree = sc.getScaleDegreeFromPitch(currNote) #what to do if scaleDegree is one? (Not in scale TODO)

    #use dictionary for scale
    AllowedIntervals = MajorIntervalsFull[scaleDegree]

    for i in range(len(EveryPossibleInterval)):
        prob[i] *= .99 if EveryPossibleInterval[i] in AllowedIntervals else .01

    return prob

def LimitToRange(prob,tonic,currNote):
    """make sure next intervals isnt too high or too low from start note
    For now ill just stop it from getting more than an octave from the otnic (TODO?)
    
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

    #find index of currtoext in everypossibleinterval #TODO handle error (do interval equivalencies)
    if currToExtName =="-P1":
        currToExtName = "P1"
    extremeIndex = EveryPossibleInterval.index(currToExtName)

    UnallowedIntervals = []

    if (isLower):
        #if currnote is lower than tonic, remove all intervals below
        #get subset of everypossibleinterval from start to extremeindex exclusive
        UnallowedIntervals.extend(EveryPossibleInterval[:extremeIndex])
    else:
        #if currnote is higher than tonic, remove all intervals above
        #get subset of everypossibleinterval from extremeindex exclusive to end
        UnallowedIntervals.extend(EveryPossibleInterval[extremeIndex+1:])


    for i in range(len(EveryPossibleInterval)):
        #is the resulting note from this too far from tonic?
        prob[i] *= .01 if EveryPossibleInterval[i] in UnallowedIntervals else .99

    return prob

def MakeStepwiseMoreLikely(prob):
    """to make stepwise motion (intervals of 2) more likely
    work out exactly what probabilities these should be
    
    @param prob current prob dist
    
    @return prob"""
    FavoredIntervals = ["m2","M2","-m2","-M2"]

    for i in range(len(EveryPossibleInterval)):
        prob[i] *= .99 if EveryPossibleInterval[i] in FavoredIntervals else .5
    return prob

def TryStepBack(prob,stepBackReq):
    """to be called on the next note in case a jump is necessary (2 intreval up or down depending on direction)
    should work regardless of scale specified outside of function
    
    @param prob current prob dist we are working with
    @param stepBackReq indicates direction to jump (>0 means jump down)
    
    @return prob dist"""
    if stepBackReq > 0:
        AllowedIntervals = ["-m2","-M2"]
    elif stepBackReq < 0:
        AllowedIntervals = ["m2","M2"]
    else:
        return prob

    for i in range(len(EveryPossibleInterval)):
        prob[i] *= .99 if EveryPossibleInterval[i] in AllowedIntervals else .01

    return prob

def SetStepBack(nextInterval):
    """returns the stepback req depending on given interval
    
    @param nextInterval the interval were about to do (already decided)
    
    @return specified step back req"""
    if(nextInterval not in ["P1","M2","M3","m2","m3","-M2","-m2","-M3","-m3"]): #small interval ragne
        #then must step back down after
        if nextInterval[0] == "-":
            return -1
        else:
            return 1
    else:
        return 0
    


def produceCF(minlen,maxlen,noteLength,tonic,intervals):
    """This function should append the specified amount of notes to a stream 
    in an order that follows the rules of the cantus firmus (see Cantus Firmus Principles)
    For now, all notes will be same length
    
    @params
    int minlen the minimum number of notes in generated cf
    int maxlen the maximum number of notes in generated cf
    int noteLength the length of each note in cf 
    string tonic which note is the tonic
    list intervals allowed intervals (major or minor) """
    #create a stream
    s = stream.Stream()
    
    #randomly choose length of cf between min and maxlen
    cfLength = random.randint(minlen,maxlen)


    #init stepback var
    stepBackReq = 0
    #append notes
    currNote= note.Note(tonic,quarterLength=noteLength)
    #start on tonic
    s.append(currNote) #sharps are # and flats are -,quarterLength 4 is whole note
    for i in range(cfLength-3):
        #initialize probability distribution
        prob=[1]*25
        #limit intervals to intervals in scale
        prob = LimitToMajorScale(prob,tonic,currNote)

        #have a check here to make sure interval doesn't go out of singers vocal range( not too far)
        prob = LimitToRange(prob,tonic,currNote)

        prob = MakeStepwiseMoreLikely(prob)

        #call stepback function
        prob = TryStepBack(prob,stepBackReq)

        print(prob)
        #give interval based on scale degree
        nextInterval = random.choices(EveryPossibleInterval,weights=prob,k=1)[0] #TODO handle 0 available choices
        print(nextInterval)
        currNote = currNote.transpose(nextInterval)

        stepBackReq = SetStepBack(nextInterval)

        print(currNote.pitch)
        s.append(currNote)

    #second to last note is 2 or 7
    tonicNote = note.Note(tonic,quarterLength=noteLength)
    notechoice = random.randint(0,1)
    if notechoice == 0:
        secondToLastNote = tonicNote.transpose("M2")
    else:
        secondToLastNote = tonicNote.transpose("-m2") #TODO unhardcode? (for 7 in minor)
    s.append(secondToLastNote)

    #end on tonic
    s.append(note.Note(tonic,quarterLength=noteLength))

    s.show() #s.write("midi",fp="onenote.midi") other possible export command

def main():
    produceCF(8,16,1,"C4",MajorIntervalsFull)


if __name__ == "__main__":
    main()



#leading tone and stepbackreq are conflicting
#so multiply by really low value instead of 0 and high instead of 1
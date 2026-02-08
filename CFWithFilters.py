"""This tests out the idea of using individual functions to define a wieghted prob dist for  each rule"""

from music21 import *
import random


#global var
EVERY_POSSIBLE_INTERVAL = ["-P8", "-M7","-m7","-M6","-m6","-P5","-D5","-P4","-M3","-m3","-M2","-m2","P1","m2","M2","m3","M3","P4","D5","P5","m6","M6","m7","M7","P8"]#12 is middle
#using D5 for tritone cuz idk (also len 25)
MajorIntervalsFull = {1:["M2","M3","P4","P5","M6","P8","-m2","-m3","-P4","-P5","-m6","-P8"],
                      2:["M2","m3","P4","P5","P8","-M2","-m3","-P4","-P5","-M6","-P8"],
                      3:["m2","m3","P4","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      4:["M2","M3","P5","M6","P8","-m2","-m3","-P4","-m6","-P8"],
                      5:["M2","M3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-m6","-P8"],
                      6:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      7:["m2"] #leading tone
                      }

MinorIntervalsFull = {1:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      2:["m2","m3","P4","m6","P8","-M2","-M3","-P5","-M6","-P8"],
                      3:["M2","M3","P4","P5","M6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      4:["M2","M3","P5","M6","P8","-m2","-m3","-P4","-m6","-P8"],
                      5:["M2","M3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-m6","-P8"],
                      6:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      7:["m2"] #leading tone
                      }

def LimitToMajorScale(weights,tonic,currNote):
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

    for i in range(len(EVERY_POSSIBLE_INTERVAL)):
        weights[i] *= 1 if EVERY_POSSIBLE_INTERVAL[i] in AllowedIntervals else 0

    return weights

def LimitToRange(weights,tonic,currNote):
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
    extremeIndex = EVERY_POSSIBLE_INTERVAL.index(currToExtName)

    UnallowedIntervals = []

    if (isLower):
        #if currnote is lower than tonic, remove all intervals below
        #get subset of everypossibleinterval from start to extremeindex exclusive
        UnallowedIntervals.extend(EVERY_POSSIBLE_INTERVAL[:extremeIndex])
    else:
        #if currnote is higher than tonic, remove all intervals above
        #get subset of everypossibleinterval from extremeindex exclusive to end
        UnallowedIntervals.extend(EVERY_POSSIBLE_INTERVAL[extremeIndex+1:])


    for i in range(len(EVERY_POSSIBLE_INTERVAL)):
        #is the resulting note from this too far from tonic?
        weights[i] *= 0 if EVERY_POSSIBLE_INTERVAL[i] in UnallowedIntervals else 1

    return weights

def MakeStepwiseMoreLikely(weights):
    """to make stepwise motion (intervals of 2) more likely
    work out exactly what probabilities these should be
    
    @param prob current prob dist
    
    @return prob"""
    FavoredIntervals = ["m2","M2","-m2","-M2"]

    for i in range(len(EVERY_POSSIBLE_INTERVAL)):
        weights[i] *= 1 if EVERY_POSSIBLE_INTERVAL[i] in FavoredIntervals else .5
    return weights

def LimitLeaps(weights, history):
    """This function will make leaps less likely, depending on long it has been since the last leap
    the probability will gradually go up over time for leaps
    This can also replace the 'make stepwise more likely function'
        
    @param weights current weight dist
    @param history int time since last jump or beginning, 0 means the last note interval was a jump"""
    
    #calculate factor based on history (maybe a good mark is 1 leap per 8 notes? (back to 1 after 8 notes))
    factor = history/8 #TODO adjust this

    #make leaps less likely
    notleaps = ["P1","M2","M3","m2","m3","-M2","-m2","-M3","-m3"] #small interval ragne

    for i in range(len(EVERY_POSSIBLE_INTERVAL)):
        #leave weight alone if it is not a leap, otherwise, multiply it by factor
        weights[i] *= 1 if EVERY_POSSIBLE_INTERVAL[i] in notleaps else factor
    return weights   

def EnsureClimaxHappens(weights,climaxCounter):
    """This function will need to:
    track the current highest note in cf,
    make sure its not the tonic 
    make sure its not repeated
        
    @param weights current weight dist
    @param climaxCounter frequency that highest note has appeared, 0 if no note has been higher than tonic"""

    UpwardsLeaps = ["P4","D5","P5","m6","M6","m7","M7","P8"]
    UpwardsAll = ["P1","m2","M2","m3","M3","P4","D5","P5","m6","M6","m7","M7","P8"]

    #case 1: 
    # starts on tonics and goes down, need to make upward leaps more likely TODO dont do this too early
    if climaxCounter == 0:
        for i in range(len(EVERY_POSSIBLE_INTERVAL)):
            weights[i] *= 1 if EVERY_POSSIBLE_INTERVAL[i] in UpwardsLeaps else .5
        return weights

    #case 2:
    #highest note has been repeated, make any upward motion more likely
    if climaxCounter > 1:
        for i in range(len(EVERY_POSSIBLE_INTERVAL)):
            weights[i] *= 1 if EVERY_POSSIBLE_INTERVAL[i] in UpwardsAll else .5
        return weights

    #case 3:
    #nearing the end, make upward leaps less likely
    #if some percentage of way to the end
    

    #otherwise leave weights unchanged
    return weights
    
def TryStepBack(weights,stepBackReq):
    """to be called on the next note in case a jump is necessary (2 intreval up or down depending on direction)
    should work regardless of scale specified outside of function
    
    @param prob current prob dist we are working with
    @param stepBackReq indicates direction to jump (>0 means step down)
    
    @return prob dist"""
    if stepBackReq > 0:
        AllowedIntervals = ["-m2","-M2"]#make thirds not leaps3,3/4,3   /3,3,4 (arpeggio)
    elif stepBackReq < 0:
        AllowedIntervals = ["m2","M2"]
    else:
        return weights

    for i in range(len(EVERY_POSSIBLE_INTERVAL)):
        weights[i] *= 1 if EVERY_POSSIBLE_INTERVAL[i] in AllowedIntervals else 0

    return weights

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
    


def produceCF(minlen,maxlen,noteLength,tonic,verbose = False):
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
    #keep track of leaps
    leapHistory = 0
    #keep track of frequency of highest note
    climaxCounter = 0
    currentClimax = note.Note(tonic,quarterLength=noteLength)
    for i in range(cfLength-3):
        #initialize probability distribution
        weights=[1]*25
        #limit intervals to intervals in scale
        weights = LimitToMajorScale(weights[:],tonic,currNote)

        #have a check here to make sure interval doesn't go out of singers vocal range( not too far)
        weights = LimitToRange(weights[:],tonic,currNote)

        #weights = MakeStepwiseMoreLikely(weights)
        weights = LimitLeaps(weights[:],leapHistory)

        if (currNote.pitch > currentClimax.pitch):
            #if current note is higher than current climax, make that the new climax and adjust counter
            currentClimax = currNote
            climaxCounter = 1
        elif (currNote.pitch == currentClimax.pitch):
            #if current note is the same then increase climaxcounter by 1
            climaxCounter +=1
        weights = EnsureClimaxHappens(weights[:], climaxCounter)

        #call stepback function
        weights = TryStepBack(weights[:],stepBackReq)

        if verbose:
            print("Weights: ", weights)
        #give interval based on scale degree
        nextInterval = random.choices(EVERY_POSSIBLE_INTERVAL,weights=weights,k=1)[0] #TODO handle 0 available choices
        if verbose:
            print("Next Interval: ", nextInterval)
        currNote = currNote.transpose(nextInterval)

        stepBackReq = SetStepBack(nextInterval)
        if stepBackReq != 0:
            #if a leap happend, reset leaphistory
            leapHistory = 0
        else:
            #else add 1
            leapHistory += 1
        if verbose:
            print("Next Note: ",currNote.pitch,"\n")
        s.append(currNote)

    #second to last note is 2 or 7
    tonicNote = note.Note(tonic,quarterLength=noteLength)
    notechoice = random.randint(0,1)
    if notechoice == 0:
        secondToLastNote = tonicNote.transpose("M2")
    else:
        secondToLastNote = tonicNote.transpose("-m2") #TODO make melody cohesive
    s.append(secondToLastNote)

    #end on tonic
    s.append(note.Note(tonic,quarterLength=noteLength))
    if verbose:
        s.show() #s.write("midi",fp="onenote.midi") other possible export command
        print("End of Cantus Firmus\n")

    return list(s)

def main():
    produceCF(8,16,1,"C4",verbose=True)


if __name__ == "__main__":
    main()




#functions yet to code
#1  avoid dissonant leaps, but may be ok if step back(add back possibility in scale)
#4  in minor, follow path of melodic minor (major up minor down)
#5 allow arpeggios
#6 need a different function to guide melody to a cadence depending on the percentage of the way to the end 
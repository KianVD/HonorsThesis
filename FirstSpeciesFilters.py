from music21 import *
#global var
EVERY_POSSIBLE_INTERVAL = ["-P8", "-M7","-m7","-M6","-m6","-P5","-D5","-P4","-M3","-m3","-M2","-m2","P1","m2","M2","m3","M3","P4","D5","P5","m6","M6","m7","M7","P8"]#12 is middle

def LimitToConsonantVertical(weights,currentFSnote,nextCFnote):
    """limits to consonant vertical intervals between cf and fs
    
    @param weights
    """
    #for each interval, calculate the note you would end up at from current fs note


    for i in range(len(weights)):
        if weights[i] != 0: #theres no point calculating it on stuff thats already 0
            associatedInterval = EVERY_POSSIBLE_INTERVAL[i]
            newnote = currentFSnote.transpose(associatedInterval)

            # then calculate if the interval between nextcfnote and that note is consonant
            newInterval = interval.Interval(nextCFnote,newnote)
            if abs(newInterval.semitones) not in [3,4,7,8,9,12]:
                weights[i] *= 0
    return weights


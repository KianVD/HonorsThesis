"""This program will be a simple starting point, to make a short melody 
with only quarter notes following the rules of the cantus firmus"""

from music21 import *
import random

#noteValue = {"C":1,"C#":2,"D":3,"D#":4,"E":} probly wont need this, can use tranpsoe
MajorIntervals = ["P1","M2","M3","P4","P5","M6","P8","-P8","-M2","-M3","-P4","-P5","-M6"] #no major 7
# MajorIntervalsUp = ["M2"] #["M2","M3","P4","P5","M6","P8"]
# MajorIntervalsDown = ["-M2"] #["-P8","-M2","-M3","-P4","-P5","-M6"]
#-M3 transposes down
#make a dictionary that has each scale degree correspond to which movements they can take
MajorIntervalsFull = {1:["M2","M3","P4","P5","M6","P8","-m2","-m3","-P4","-P5","-m6","-P8"],#take out p1 for one
                      2:["M2","m3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-M6","-P8"],
                      3:["m2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      4:["M2","M3","P5","M6","P8","-m2","-m3","-P4","-m6","-P8"], #P4 and -P5 not possible
                      5:["M2","M3","P4","P5","M6","P8","-M2","-m3","-P4","-P5","-m6","-P8"],
                      6:["M2","m3","P4","P5","m6","P8","-M2","-M3","-P4","-P5","-M6","-P8"],
                      7:["m2"] #leading tone
                      }
MajorIntervalsUp = {1 :["M2"],#take out p1 for one
                      2:["M2"],
                      3:["m2"],
                      4:["M2"], #P4 and -P5 not possible
                      5:["M2"],
                      6:["M2"],
                      7:["m2"] #leading tone
                      }
MajorIntervalsDown = {1 :["-m2"],#take out p1 for one
                      2:["-M2"],
                      3:["-M2"],
                      4:["-m2"], #P4 and -P5 not possible
                      5:["-M2"],
                      6:["-M2"],
                      7:["-M2"] #leading tone
                      }



#shoudl there be a range specified?
#dont forget to step back on jump


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
        #first figure out scale degree
        sc = scale.MajorScale(tonic)
        scaleDegree = sc.getScaleDegreeFromPitch(currNote)
        print(scaleDegree)

        #choose next interval
        if(stepBackReq > 0):
            #must choose an interval that goes down from last one
            nextInterval = MajorIntervalsDown[scaleDegree][0] #TODO unhardcode this
            #then clear stepBackReq
            stepBackReq = 0
        elif(stepBackReq < 0):
            #must choose an interval that goes up from last one
            nextInterval = MajorIntervalsUp[scaleDegree][0] #TODO unhardcode this
            #then clear stepBackReq
            stepBackReq = 0
        else:
            #give interval based on scale degree
            nextInterval = random.choice(MajorIntervalsFull[scaleDegree]) #TODO unhardcode

        currNote = currNote.transpose(nextInterval)
        #have a check here to make sure interval doesn't go out of singers vocal range( not too far)
        if(nextInterval not in ["P1","M2","M3","m2","m3","-M2"]):#TODO do down jumps too
            #then must step back down after
            if nextInterval[0] == "-":
                stepBackReq = -1
            else:
                stepBackReq = 1

        print(currNote)
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
    produceCF(8,16,1,"C4",MajorIntervals)


if __name__ == "__main__":
    main()


#footnote; for making it mostly conjunct motion, I could weight the random choice so it is more likely to choose conjunct motion
#or I could cap the jumps to 1 or 2 times per cf, and once the cf is out of jumps it cant jump again
#TODO now cantus firmus is only missing direction, mostly conjunct motion, minor keys, arpeggios, 
#make it less likely to leap right after leap, then gradually increase likelihood
#filter to probabilities (replace stepbackreq)
#deal with all 0 prob
#dynamically update pitch range, pull up limits
#some percentage close to the end (maybe early stopping once past lower limit)
#probability array



"""takes a cantus firmus and first species results and finds the information we looking for
puts data into a csv analysisResults"""

import json
import csv

#data to find for leap groups of cantus firmus:
# 1) length
# 2) number of leaps in each cantus firmus (N/A for combined, all cantus firmus of length)
# 3) number of cantus firmuses (number of files in folder) (these will all add up to top row)
# 4) avg number of first species counterpoints (average lines per file)
# 5) variation of number of first species counterpoints (variation(lines per file))
# 6) standard deviation of number of first species counterpoints (sqrt(variance))
# 7) avg number of first species counterpoints starting on the tonic
# 8) variation of number of first species counterpoints starting on the tonic
# 9) standard deviation of number of first species counterpoints starting on the tonic
# 10) avg number of first species counterpoints starting on the third
# 11) variation of number of first species counterpoints starting on the third
# 12) standard deviation of number of first species counterpoints starting on the third
# 13) avg number of first species counterpoints starting on the fifth
# 14) variation of number of first species counterpoints starting on the fifth
# 15) standard deviation of number of first species counterpoints starting on the fifth
# 16) avg number of first species counterpoints all containing a tie
# 17) variation of number of first species counterpoints all containing a tie
# 18) standard deviation of number of first species counterpoints all containing a tie
# 19) avg number of first species counterpoints all not containing a tie
# 20) variation of number of first species counterpoints all not containing a tie
# 21) standard deviation of number of first species counterpoints all not containing a tie

#in the future, we can exclude cantus firmus or first species with too many leaps, just have to figure out the cutoff 
# (maybe a different cutoff for each length) (that would be better coded into the rules)

#needs the file from generating all cf and the folder for generating all fs on the cfs
CF_MELODIES = "generated_melodies.txt" #every melody in this file must have a corresponding file in results folder for all the fs on that melody
RESULTS_FOLDER = "results"
OUT = "analysisResults.csv"


def melodyToName(melody):
    melodyNotes = melody.split(",")
    return "_".join(melodyNotes)


cfdicts = []
length = 0
out_data = [["length","leapCount","cfCount","avgfs","varfs","stdevfs","avgfs1","varfs1","stdevfs1","avgfs3","varfs3","stdevfs3","avgfs5","varfs5","stdevfs5","avgfsTie","varfsTie","stdevfsTie","avgfsNoTie","varfsNoTie","stdevfsNoTie"]]
with open(CF_MELODIES, "r") as f:
    #get dicts into a list
    for line in f:
        cfdict = json.loads(line.strip())
        cfdicts.append(cfdict)
        if length == 0: #set length
            length = len(cfdict["melody"].split(","))
    


#loop through lengths of leaps (first all lengths, then 0,1,2,etc):
currLeapNumber = -1
while True:
    dataFound = False
    cfcount = 0
    totalfscount = 0
    for cfdict in cfdicts:
        if currLeapNumber == -1:
            dataFound = True
            #accumulate data to find avg and var
            cfcount += 1
            with open("results/" + melodyToName(cfdict["melody"]),"r") as f: #open fs file for specific cf
                fscount = 0
                for line in f:
                    fscount += 1
                    fsdict = json.loads(line.strip()) #TODO get the rest of data
                totalfscount += fscount
            
        else:
            #compare currLeapnum
            if cfdict["leapCount"] == currLeapNumber:
                dataFound = True
                #accumulate data to find avg and var
                cfcount += 1
                with open("results/" + melodyToName(cfdict["melody"]),"r") as f: #open fs file for specific cf
                    fscount = 0
                    for line in f:
                        fscount += 1
                        fsdict = json.loads(line.strip()) #TODO get the rest of data
                    totalfscount += fscount


                
    if not dataFound:
        break #no cf has this leap count
    if currLeapNumber == -1:
        leapCount = "N/A"
    else:
        leapCount = str(currLeapNumber)
    #get all data into list and add to data
    out_data.append([length,leapCount,cfcount,totalfscount/cfcount])
    currLeapNumber += 1


with open(OUT,"w",newline='') as f:
    writer = csv.writer(f)
    writer.writerows(out_data)

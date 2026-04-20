"""takes a cantus firmus and first species results and finds the information we looking for
puts data into a csv analysisResults"""

import json
import csv
import math

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



class DataAnalyzer():
    def __init__(self):
        pass
    def melodyToName(self,melody):
        melodyNotes = melody.split(",")
        return "_".join(melodyNotes)

    def analyze(self,cf_melodies,results_folder,out,pop):
        """
        fully analyze data to find values above
        
        @param
        cf_melodies filename with generated cf melody jsons
        results_folder folder name with fs generated files for each cf, must have a file for each melody in cf_melodies
        out filename to output results csv to
        pop bool whether the given cf melodies is the entire population or not"""
        cfdicts = []
        length = 0
        out_data = [["length","leapCount","cfCount","avgfs","varfs","stdevfs","avgfs1","varfs1","stdevfs1","avgfs3","varfs3","stdevfs3","avgfs5","varfs5","stdevfs5","avgfsTie","varfsTie","stdevfsTie","avgfsNoTie","varfsNoTie","stdevfsNoTie"]]
        with open(cf_melodies, "r") as f:
            #get dicts into a list
            for line in f:
                cfdict = json.loads(line.strip())
                cfdicts.append(cfdict)
        #set length
        length = len(cfdicts[0]["melody"].split(","))
            


        #loop through lengths of leaps (first all lengths, then 0,1,2,etc):
        leap_counts = set(cfdict["leapCount"] for cfdict in cfdicts)
        #loop through -1,0,up to the max possible leaps (just put length for now, well over max always)
        for currLeapNumber in [-1] + sorted(leap_counts):
            cfcount = 0
            fscountData = [[],[],[],[],[],[]]
            totalfscount = [0] * 6#0 is all, 1 is 1, 2 is 3, 3 is 5, 4 is tie, 5 is no tie
            for cfdict in cfdicts:
                #consider all leapcounts
                if currLeapNumber == -1 or cfdict["leapCount"] == currLeapNumber: #only accumulate data if currLeapNumber is -1 (accumulate all data) or leapCount is equal to current leapnum (gets subset of data)
                    #accumulate data to find avg and var
                    cfcount += 1
                    with open(results_folder + "/" + self.melodyToName(cfdict["melody"]),"r") as f: #open fs file for specific cf
                        fscount = [0] * 6
                        for line in f:
                            fscount[0] += 1
                            fsdict = json.loads(line.strip())
                            if fsdict["startingNote"] == 1:
                                fscount[1] += 1
                            elif fsdict["startingNote"] == 3:
                                fscount[2] += 1
                            elif fsdict["startingNote"] == 5:
                                fscount[3] += 1
                            if fsdict["tieUsed"] == True:
                                fscount[4] += 1
                            elif fsdict["tieUsed"] == False:
                                fscount[5] += 1
                            else:
                                print("json bool parsing error")
                        for i in range(len(fscount)):
                            fscountData[i].append(fscount[i])#append count of fs for this cf to list of fscounts
                            totalfscount[i] += fscount[i] #append fscounts

            #get leapCount value for writing to file
            if currLeapNumber == -1:
                leapCount = "N/A"
            else:
                leapCount = str(currLeapNumber)

            avgfs = [0]*6
            varfs = [0]*6
            denom = cfcount #popoulation variance
            if not pop:#sample variance
                denom -= 1
            #get avg and var for each subset
            for i in range(len(totalfscount)):
                avgfs[i] = totalfscount[i]/cfcount
                #find variance with avgfs now
                numerator_sum = 0
                for fscount in fscountData[i]:
                    se =  (fscount - avgfs[i])** 2
                    numerator_sum += se

                varfs[i] = numerator_sum/ denom

            out_row = [length,leapCount,cfcount]
            for i in range(len(totalfscount)):
                out_row.extend([avgfs[i],varfs[i],math.sqrt(varfs[i])])

            out_data.append(out_row)


        with open(out,"w",newline='') as f:
            writer = csv.writer(f)
            writer.writerows(out_data)

    def prepare(self,cf_melodies,results_folder,out):
        """prepare cf data in csv to be analyzed in excel (for boxplot)"""
        cfdicts = []
        out_data = [["cfname","leapCount","fscount"]]
        with open(cf_melodies, "r") as f:
            #get dicts into a list
            for line in f:
                cfdict = json.loads(line.strip())
                cfdicts.append(cfdict)


        for cfdict in cfdicts:
            #accumulate data to find avg and var
            cfname = self.melodyToName(cfdict["melody"])
            with open(results_folder + "/" + self.melodyToName(cfdict["melody"]),"r") as f: #open fs file for specific cf
                fscount = 0
                for line in f:
                    fscount += 1
                out_data.append([cfname,cfdict["leapCount"],fscount])


        with open(out,"w",newline='') as f:
            writer = csv.writer(f)
            writer.writerows(out_data)



def main():

    #needs the file from generating all cf and the folder for generating all fs on the cfs
    cf_melodies = "generated_melodies10.txt" #every melody in this file must have a corresponding file in results folder for all the fs on that melody
    results_folder = "results10"
    out = "analysisResults10.csv"
    
    da = DataAnalyzer()
    da.analyze(cf_melodies,results_folder,out,True)#True for population, False for sample
    #da.prepare(cf_melodies,results_folder,"preparedData.csv")
    


if __name__ == "__main__":
    main()

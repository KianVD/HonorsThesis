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
                if length == 0: #set length
                    length = len(cfdict["melody"].split(","))
            


        #loop through lengths of leaps (first all lengths, then 0,1,2,etc):
        currLeapNumber = -1
        #loop through -1,0,up to the max possible leaps (just put length for now, well over max always)
        for _ in range(length):
            cfcount = 0
            fscounts = []
            totalfscount = 0
            for cfdict in cfdicts:
                if currLeapNumber == -1:
                    #accumulate data to find avg and var
                    cfcount += 1
                    with open(results_folder + "/" + self.melodyToName(cfdict["melody"]),"r") as f: #open fs file for specific cf
                        fscount = 0
                        for line in f:
                            fscount += 1
                            fsdict = json.loads(line.strip()) #TODO get the rest of data
                        fscounts.append(fscount)#append count of fs for this cf to list of fscounts
                        totalfscount += fscount

                    
                else:
                    #compare currLeapnum
                    if cfdict["leapCount"] == currLeapNumber:
                        #accumulate data to find avg and var
                        cfcount += 1
                        with open(results_folder + "/" + self.melodyToName(cfdict["melody"]),"r") as f: #open fs file for specific cf
                            fscount = 0
                            for line in f:
                                fscount += 1
                                fsdict = json.loads(line.strip()) #TODO get the rest of data
                            fscounts.append(fscount)#append count of fs for this cf to list of fscounts
                            totalfscount += fscount        
            if currLeapNumber == -1:
                leapCount = "N/A"
            else:
                leapCount = str(currLeapNumber)
            #get all data into list and add to data
            #if there were no cf for this leap count then just skip writing that row
            if cfcount != 0:
                avgfs = totalfscount/cfcount
                #find variance with avgfs now
                numerator_sum = 0
                for fscount in fscounts:
                    se =  (fscount - avgfs)** 2
                    numerator_sum += se
                denom = cfcount #popoulation variance
                if not pop:#sample variance
                    denom -= 1
                varfs = numerator_sum/ denom


                out_data.append([length,leapCount,cfcount,avgfs,varfs,math.sqrt(varfs)])
            #increment leap
            currLeapNumber += 1


        with open(out,"w",newline='') as f:
            writer = csv.writer(f)
            writer.writerows(out_data)

    def prepare(self,cf_melodies,results_folder,out):
        """prepare cf data in csv to be analyzed in excel (for boxplot?)"""
        cfdicts = []
        length = 0
        out_data = [["cfname","leapCount","fscount"]]
        with open(cf_melodies, "r") as f:
            #get dicts into a list
            for line in f:
                cfdict = json.loads(line.strip())
                cfdicts.append(cfdict)
                if length == 0: #set length
                    length = len(cfdict["melody"].split(","))


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
    cf_melodies = "generated_melodies8.txt" #every melody in this file must have a corresponding file in results folder for all the fs on that melody
    results_folder = "results8"
    out = "analysisResults.csv"
    
    da = DataAnalyzer()
    da.analyze(cf_melodies,results_folder,out,True)#True for population, False for sample
    #da.prepare(cf_melodies,results_folder,"preparedData.csv")
    


if __name__ == "__main__":
    main()

"""a standalone class to produce tree of cantus firmus based on fux fixed rules
rules will all be methods of cfproducer class"""

class CFProducer():
    def __init__(self,epi):
        self.every_possible_interval = epi

    def produceCF(n,verbose=False):
        """create and show cantus firmus
        return list of notes"""

        if verbose:
            print(f"generating cantus firmus of length {n}")

        




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
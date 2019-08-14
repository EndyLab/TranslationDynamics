import pandas
import numpy as np

def totalRibosomeCollisions(df,tRNAid,ribosomeIDList):
    rib=np.zeros(len(ribosomeIDs))
    timeavg=np.zeros(len(ribosomeIDs))
    for index, row in df.iterrows():
        if row["reactantA"] != tRNAid:
            print(row["reactantA"])
            break
        for index, ribosomeID in ribosomeIDList:
            if row["reactantB"]==ribosomeID:
                rib[index]+=1
                timeavg[index]+=row["time"]
    timeavg=np.array(timeavg)/np.array(rib)
    return rib, timeavga
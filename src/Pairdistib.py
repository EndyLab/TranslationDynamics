import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import sys

def calcPairDistribFunc(path,expt_start,expt_end,species1,species2):
    df_outputs = pd.read_csv(path+"outputMolPosList.txt",sep=" ",header=None) #Add batch processing here potentially
    distance = list()
    for expt_num, row in df_outputs.iterrows():
        succincorp_count = 0
        rxn17_count = 0
        rxn21_count = 0
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                my_cols=["timestep","species","_","x","y","z","id"]
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols)
                df_species1=df[df['species']==species1]
                df_species1=df_species1[['x','y','z']]
                df_species2=df[df['species']==species2]
                df_species2=df_species2[['x','y','z']]

                for i, coords in df_species1.iterrows():
                    distance.append(np.mean(np.sqrt(np.square(df_species2-coords.values).sum(axis=1)).values))
            except:
                print("Error on expt ", expt_num)
    #plt.hist(distance)
    print(np.mean(distance))
    return np.mean(distance)

path = '/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/data/'
data = '190320_1830'
gr=[0.6,1.0,1.5,2.0,2.5,3.0]
avg_tRNARibDist = list()
for i in range(1,len(gr)+1):
    avg_tRNARibDist.append(calcPairDistribFunc(path+data+'/',50*i,50*(i+1),3,5))
avg_tRNARibDist = np.array(avg_tRNARibDist)
print(avg_tRNARibDist)


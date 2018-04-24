import pandas as pd
import numpy as np
import sys
import math

def countRibosomeCollisions(df,tRNAid,ribosomeIDList):
    df = df.sort_values(by=['reactantA'])
    rib=np.zeros(len(ribosomeIDList))
    timeavg=np.zeros(len(ribosomeIDList))
    for index, row in df.iterrows():
        if row["reactantA"] != tRNAid:
            print(row["reactantA"])
            break
        for index, ribosomeID in enumerate(ribosomeIDList):
            if row["reactantB"]==ribosomeID:
                rib[index]+=1
                timeavg[index]+=row["time"]
    timeavg=np.array(timeavg)/np.array(rib)
    return rib, timeavg

#Module for analysis of number of wrong collisions before correct tRNA reaches ribosome 1.4 times
#Produces graph of distribution of number of collisions in between two correct events
#Need to check to see how far the poisson (power law?) distribution is for caged events vs. free diffusing/mixing events
#to identify anomalies/spatial effects other than just being rare events being sampled.
#or we find out that the distribution is same for each ribosome, just spends less time near the ribosome.
#Fluitt uses "average", but really we have a poisson sampling rate where "avg" less meaningful
#Rewrite this code to just do calculation of riboosme&tRNA count w/ 1 pass of df


def countIncorrectRibosomeCollisionsFast(df, tRNA_IDList, ribosome_IDList):
    df=df.sort_values(['reactantB','time'], ascending=[True,True])
    IncorrectNumColMatrix=np.zeros([len(tRNA_IDList),len(ribosome_IDList)])
   
    IncorrectCollisions_tr = list()
    for t in range(len(tRNA_IDList)):
        IncorrectCollisions_tr.append(list())
        for r in range(len(ribosome_IDList)):
            IncorrectCollisions_tr[t].append(list())
    print(IncorrectCollisions_tr)

    for r_index, ribosomeID in enumerate(ribosome_IDList):
        print(r_index)
        df_i = df.loc[df['reactantB']==ribosomeID]
        for index, row in df_i.iterrows():            
            for t_index, tRNAID in enumerate(tRNA_IDList):
                if row["reactantA"]!=tRNAID:
                    IncorrectNumColMatrix[t_index, r_index]+=1;
                elif row["reactantA"]==tRNAID:
                    IncorrectCollisions_tr[t_index][r_index].append(IncorrectNumColMatrix[t_index, r_index])
                    IncorrectNumColMatrix[t_index, r_index] = 0
    return IncorrectCollisions_tr


def timeSplitter(df, start_time=0, time_interval=0.01, scale="linear",logscalestart=-3):
    df=df.sort_values(['time'], ascending=[True])
    end_time = df.iloc[df.shape[0]-1]['time']

    if scale=="linear":
        time_arr = np.arange(start_time,end_time+time_interval,time_interval)
    elif scale=="log":
        time_arr = np.logspace(logscalestart,math.ceil(np.log10(end_time)),1+abs(logscalestart)+math.ceil(np.log10(end_time)))

    timesplitdf = df.groupby(pd.cut(df["time"],time_arr))
    groupkeys = [interval for interval, timesplitdf_i in timesplitdf]
    timesplitdf_list = list()
    for key in groupkeys:
        timesplitdf_list.append(timesplitdf.get_group(key))

    return timesplitdf_list









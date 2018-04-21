import pandas
import numpy as np

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

def countIncorrectRibosomeCollisions(df, tRNAidList, ribosomeidList):
    df=df.sort_values(['reactantB','time'], ascending=[True,True])
    collisionCountTot=list()
    collisionCountDistrib=list()
    ribosomeCountDistrib=list()
    for ribosomeID in ribosomeidList:
        for tRNAid in tRNAidList:
            collisionCount =0
            for index, row in df.iterrows():
                if row["reactantB"]==ribosomeID:
                    if row["reactantA"]!=tRNAid:
                        collisionCount+=1
                    if row["reactantA"]==tRNAid:
                        collisionCountTot.append(collisionCount)
                        collisionCount=0
            collisionCountDistrib.append(collisionCountTot)
            collisionCountTot=list()
        ribosomeCountDistrib.append(collisionCountDistrib)
        print(ribosomeID)
        collisionCountDistrib=list()
    return ribosomeCountDistrib
    #update this method to just adding tRNA, rib. pair to a matrix in one pass.
    #Can just check whether reacA and reacB fall in the matrix i make.

def countIncorrectRibosomeCollisionsFast(df, tRNA_IDList, ribosome_IDList):
    df=df.sort_values(['reactantB','time'], ascending=[True,True])
    IncorrectNumColMatrix=np.ones([len(tRNA_IDList),len(ribosome_IDList)])*-100
    for r_index, ribosomeID in enumerate(ribosome_IDList):
        df_i = df.loc[df['reactantB']==ribosomeID]
        for index, row in df_i.iterrows():
            CollisionCount = np.zeros([len(tRNA_IDList)])
            for t_index, tRNAID in enumerate(tRNA_IDList):
                if row["reactantA"]==tRNAID:
                    IncorrectNumColMatrix[t_index, r_index]
        print(ribosomeID)
    return IncorrectNumColMatrix



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import sys

#get the particle distances
def calcPairDistances(path,expt_start,expt_end,species1,species2, max_distvalue):
    print(species1)
    df_outputs = pd.read_csv(path+"outputMolPosList.txt",sep=" ",header=None) #read the file that has all the names of molpos files
    distance = list()
    for expt_num, row in df_outputs.iterrows():
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                my_cols=["timestep","species","_","x","y","z","id"] #give a header name to each column
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols) #read the columns in each file
                df_species1=df[df['species']==species1] #identify the rows of species-1
                df_species1=df_species1[['x','y','z']] #identify in the rows of species-1 the species-1 coordinates
                df_species2=df[df['species']==species2]
                df_species2=df_species2[['x','y','z']]
                for i, coords in df_species1.iterrows():
                    distance_i = list()
                    for j, coords2 in df_species2.iterrows():
                        dist = coords2.values-coords.values
                        for dim in range(0,3):
                            if dist[dim]>max_distvalue:
                                dist[dim] = dist[dim]-max_distvalue*2
                            elif dist[dim] < -1*max_distvalue:
                                dist[dim] = dist[dim]+max_distvalue*2
                        dist_mag = np.sqrt(np.square(dist).sum())
                        if dist_mag<(max_distvalue*3**(0.5)):
                            distance_i.append(dist_mag)
                    distance.append(min(distance_i))
            except:
                print("Error on expt ", expt_num)
    return distance
    


path = '/Users/Akshay/Documents/TranslationDynamics/data/'
data = '191010_1846' #'200708_1100'

gr=[0.6,1.0,1.5,2.0,2.5,3.0] #0.6,1.0,1.5,2.0,2.5,3.0]# doubling rate
vox =[0.101*1/0.0059,0.0929*1/0.0059,0.0842*1/0.0059,0.0774*1/0.0059,0.072*1/0.0059,0.0677*1/0.0059] #0.101*1/0.0059,0.0929*1/0.0059,0.0842*1/0.0059,0.0774*1/0.0059,0.072*1/0.0059,0.0677*1/0.0059] 
expnum = 100

max_dist = []
for i in range(len(vox)):
     max_dist.append(vox[i]/2)
print('max_dist, ', max_dist)

dist = {}
for i in range(0,len(gr)):
    print('gr:', gr[i])
    dist[gr[i]] = calcPairDistances(path+data+'/',expnum*i,expnum*(i+1),3,11, max_dist[i]) #experiment number hardcoded & species hardcoded (3,11)


print('Average distances: ',np.average(dist[0.6]), ' ', np.average(dist[1.0]),' ',np.average(dist[1.5]),' ',np.average(dist[2.0]),' ',np.average(dist[2.5]),' ',np.average(dist[3.0]))
print('Standard deviations: ',np.std(dist[0.6])/np.sqrt((len(dist[0.6])-1)),' ',np.std(dist[1.0])/np.sqrt((len(dist[1.0])-1)),' ',np.std(dist[1.5])/np.sqrt((len(dist[1.5])-1)),' ',np.std(dist[2.0])/np.sqrt((len(dist[2.0])-1)),' ',np.std(dist[2.5])/np.sqrt((len(dist[2.5])-1)),' ',np.std(dist[3.0])/np.sqrt((len(dist[3.0])-1)))


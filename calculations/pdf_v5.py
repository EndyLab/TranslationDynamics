import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import sys

#get the particle distances
def calcPairDistribFunc(path,expt_start,expt_end,species1,species2):
    print(species1)
    df_outputs = pd.read_csv(path+"outputMolPosList.txt",sep=" ",header=None) #read the file that has all the names of molpos files
    distance = list()
#     print 'here1'
    for expt_num, row in df_outputs.iterrows():
        succincorp_count = 0
        rxn17_count = 0
        rxn21_count = 0
#         print 'here2'

        if(expt_num>=expt_start and expt_num<expt_end): #it seems there are 50 experiments per growth rate
            try:
                my_cols=["timestep","species","_","x","y","z","id"] #give a header name to each column
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols) #read the columns in each file
                df_species1=df[df['species']==species1] #identify the rows of species-1
                df_species1=df_species1[['x','y','z']] #identify in the rows of species-1 the species-1 coordinates
                df_species2=df[df['species']==species2]
                df_species2=df_species2[['x','y','z']]
                for i, coords in df_species1.iterrows():
                	for j, coords2 in df_species2.iterrows():
                		distance.append(np.sqrt(np.square(coords2.values-coords.values).sum(axis=1)).values)
            except:
                print("Error on expt ", expt_num)
    #plt.hist(distance)
    #print(distance)
    #return np.mean(distance)
    return distance
    
### make dictionary
def initialize_counts_dic(binsval):
	#initialize the "internal" dict counts
	count_dic={}
	for ii in range(binsval+1):
		count_dic[ ii ] = 0
	return count_dic      
	

def histgen(distvalues, dr, max_distvalue, voxlength ):
	binsval = int(voxlength/dr)
	histdict = initialize_counts_dic(binsval)
	totcount = 0
	for i in range(len(distvalues)):
		if distvalues[i]>max_distvalue:
			dum1 = 2.*max_distvalue-distvalues[i]
			dum = int(abs(dum1//dr))
		else:
			dum = int(distvalues[i]//dr)
		if dum <= binsval:
			histdict[dum] += 1
			totcount += 1
	return (histdict, totcount)

def pdfgen(voxlength, dr, minval, numdens, histogram,numexp):
	pdfvalgr = []
	binsval = int(voxlength/dr)
	print('binsval', binsval)
	for i in range(binsval+1):
		drval=(i+0.5)*dr
		if i < minval:
			tuple=drval,0
		else:
			volshell = 4.*np.pi*dr/2.*((i+1)*dr/2.)**2
# 			print i
# 			print "grdict[i]", grdict[i]
# 			print 'volshell', volshell
			dum2 = histogram[i]/numexp/(numdens*volshell)
			tuple = drval,dum2
		pdfvalgr.append(tuple)
	return (pdfvalgr)      

path = '/Users/Akshay/Documents/TranslationDynamics/data/'
data = '191010_1846'
#gr=[0.6]# doubling rate
#vox =[17.118644067796613] 
#expnum = 10
gr=[3.0] #0.6,1.0,1.5,2.0,2.5,3.0]# doubling rate
vox =[0.0677*1/0.0059] #0.101*1/0.0059,0.0929*1/0.0059,0.0842*1/0.0059,0.0774*1/0.0059,0.072*1/0.0059,0.0677*1/0.0059] 
expnum = 100
max_dist = []
for i in range(len(vox)):
    max_dist.append(3.**(0.5)*(vox[i]/2))
print(max_dist)

avg_tRNARibDist = list()
dist={}

for i in range(0,len(gr)):
    if i<len(gr):
    	print('gr:', gr[i])
    	dist[gr[i]] = calcPairDistribFunc(path+data+'/',expnum*i,expnum*(i+1),3,11) #experiment number hardcoded & species hardcoded (3,11)
bins = 40
dr = vox[0]/bins

histgr = {}
totcountdict = {}
pdfval ={}

for jj in range(len(gr)):
# for jj in xrange(1):
	print(jj)
	runs = expnum
	histgr[gr[jj]], totcountdict[gr[jj]] = histgen(dist[gr[jj]], dr, max_dist[jj], vox[jj])
	minval = int(min(dist[gr[jj]])//dr)
	numdens = totcountdict[gr[jj]]/runs/(4./3.*np.pi*(max_dist[jj]/2)**3)
	pdfval[gr[jj]] = pdfgen( vox[jj], dr, minval, numdens, histgr[gr[jj]],expnum)

for jj in range(len(gr)):
	print( pdfval[gr[jj]])

print(pdfval[gr[0]][0][0])

#print('hi',dist[0.6])
#plt.hist(dist[0.6],density=True)
#plt.savefig('test111.jpg')
#print(np.average(dist[0.6]))#,np.average(dist[1.0]),np.average(dist[1.5]),np.average(dist[2.0]),np.average(dist[2.5]),np.average(dist[3.0]))
#print(np.std(dist[0.6]))#/np.sqrt((len(dist[0.6])-1)),np.std(dist[1.0])/np.sqrt((len(dist[1.0])-1)),np.std(dist[1.5])/np.sqrt((len(dist[1.5])-1)),np.std(dist[2.0])/np.sqrt((len(dist[2.0])-1)),np.std(dist[2.5])/np.sqrt((len(dist[2.5])-1)),np.std(dist[3.0])/np.sqrt((len(dist[3.0])-1)))


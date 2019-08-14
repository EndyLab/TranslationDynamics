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
                    distance.append(np.mean(np.sqrt(np.square(df_species2-coords.values).sum(axis=1)).values))
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
	for ii in xrange(binsval+1):
		count_dic[ ii ] = 0
	return count_dic      
	

def histgen(distvalues, dr, max_distvalue, voxlength ):
	binsval = int(voxlength/dr)
	histdict = initialize_counts_dic(binsval)
	totcount = 0
	for i in xrange(len(distvalues)):
		if distvalues[i]>max_distvalue:
			dum1 = 2.*max_distvalue-distvalues[i]
			dum = int(abs(dum1//dr))
		else:
			dum = int(distvalues[i]//dr)
		if dum <= binsval:
			histdict[dum] += 1
			totcount += 1
	return (histdict, totcount)

def pdfgen(voxlength, dr, minval, numdens, histogram ):
	pdfvalgr = []
	binsval = int(voxlength/dr)
	print 'binsval', binsval
	for i in xrange(binsval+1):
		drval=(i+0.5)*dr
		if i < minval:
			tuple=drval,0
		else:
			volshell = 4.*np.pi*dr/2.*((i+1)*dr/2.)**2
# 			print i
# 			print "grdict[i]", grdict[i]
# 			print 'volshell', volshell
			dum2 = histogram[i]/50./(numdens*volshell)
			tuple = drval,dum2
		pdfvalgr.append(tuple)
	return (pdfvalgr)      

path = '/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/data/'
data = '/190724_1711'
#gr=[0.6,1.0,1.5,2.0,2.5,3.0]# doubling rate
#vox =[0.1008553156299825, 0.09292614340673645, 0.08424111219214989, 0.07738620566244644, 0.07199644075126958, 0.06767802200013741] 
gr = [0.6,3.0]
vox = [0.1008553156299825,0.06767802200013741]
expnum = [150.0, 150.0]
max_dist = []
for i in xrange(len(vox)):
    max_dist.append(3.**(0.5)*(vox[i]/2))
print max_dist

avg_tRNARibDist = list()
dist={}

# for i in xrange(len(gr)):
for i in xrange(0,len(gr)):
    if i<len(gr):
    	print 'gr:', gr[i]
    	dist[gr[i]] = calcPairDistribFunc(path+data+'/',150*i,150*(i+1),3,5)
    else:
    	print 'last'
    	print 'gr:', gr[i]
    	dist[gr[i]] = calcPairDistribFunc(path+data+'/',150*i,150*(i+1)-2,3,5)
#     print "i", i


bins = 80
dr = vox[0]/bins

histgr = {}
totcountdict = {}
pdfval ={}

for jj in xrange(len(gr)):
# for jj in xrange(1):
	print jj
	if jj == len(gr)-1:
		runs = expnum[1]
	else:
		runs = expnum[0]
	histgr[gr[jj]], totcountdict[gr[jj]] = histgen(dist[gr[jj]], dr, max_dist[jj], vox[jj])
	minval = int(min(dist[gr[jj]])//dr)
	numdens = totcountdict[gr[jj]]/runs/(4./3.*np.pi*(max_dist[jj]/2)**3)
	pdfval[gr[jj]] = pdfgen( vox[jj], dr, minval, numdens, histgr[gr[jj]] )

for jj in xrange(len(gr)):
	print pdfval[gr[jj]]
	print
	print
	
# maxval = {{0.06, 0.05206255378605083}, {1., 
#     0.054587751820479306}, {1.5, 0.05271471823023274}, {2., 
#     0.046474095678377896}, {2.5, 0.04359302707399332`}, {3., 
#     0.03893426729339011}};
import pandas as pd
import numpy as np
import sys
import math
import pickle as pkl
import glob


def readSimData(path):
    """Reads reaction_log output csv file from a Smoldyn simulation and converts to a dataframe
    
    Args:
        path (string): Path to reaction_log output csv/xls file
    
    Returns:
        df (dataframe): dataframe containing reaction_log data. 
        Rows: One for each reaction/collision that took place
        Columns: 
            time: describes the time of reaction
            rxn: gives the reaction name
            x: x coordinate of reaction
            y: y coordinate of reaction
            z: z coordinate of reaction
            reactantA: Gives the id of the first reactant defined
            reactantB: Gives the id of the second reactant defined
            productA: Gives the id of the first product defined (usually same as reactant A)
            productB: Gives the id of the second product defined (usually same as reactant B)
    """
    df = pd.read_csv("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/data/expt-0-Reactions-20181018.csv",sep=" ",
        header=None,names=list(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]))

    return df



def totalCollisions(path):
    """
    Calculates the total number of collisions between all molecules of any type based on a defined "min_delta_time",
    or the minimum time that must lapse before an overlap between two particles is considered a collision again.
    
    Arguments:
        path {string} -- Path to the smoldyn output file that records all overlap events that occured between particles
    
    Returns:
        [List] -- [List containing 1. original length of collision file; 2. length after discarding collisions that occured
        before some set time (to avoid artifacts from extra collisions at startup due to overlap). 3. Total number of collisions 
        between all particles in the provided simulation]
    """
    min_delta_time = 1e-9
    print(path)
    df_chunker = pd.read_csv(path,delimiter=" ",header=None,chunksize=500000)
    overall_return_array = list([0,0,0])
    for df in df_chunker:
        returnArray=list()
        df.columns=["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]
        returnArray.append(df.shape[0])
        df = df[df['time'] > 1e-7]  #Drop first 100 nanoseconds due to overlap of spheres at startup causing increased rxns
        #df = df.sort_values(by=['time','reactantA'])
        df = df[['time','reactantA','reactantB']]

        df = df.iloc[0:] #test different time lengths if desired
        returnArray.append(df.shape[0])

        lookup = {}
        collision=0
     
        for index, row in df.iterrows():
            reacA_i = row["reactantA"] 
            reacB_i = row["reactantB"]
            time_i = row['time']
            
            #Check if the pair collision occured in the last min_delta_time, and if not, add the collision to the count
            if ((reacA_i,reacB_i) not in lookup) or ((time_i-lookup[(reacA_i,reacB_i)][0] > min_delta_time)): 
            #Note, second part of or statement only evaluated if first is false, i.e. reacA and reacB in lookup.
                collision+=1
                lookup[(reacA_i,reacB_i)] = [time_i]
                lookup[(reacB_i,reacA_i)] = [time_i]

        returnArray.append(collision)
        overall_return_array = np.add(overall_return_array, returnArray)
        print(1)
    return overall_return_array

def mixTime(path):
    # df = pd.read_csv(path,delimiter=" ",header=None,names=(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]))
    
    # mixtimes=list()

    # df = df[['time','reactantA']]
    # df = df[df['time'] > 1e-7]  #Drop first 100 nanoseconds due to overlap of spheres at startup causing increased rxns

    # df = df.sort_values(by=['reactantA','time'])
    # df_group = df.groupby('reactantA')
    # while(len(df_group)==42):
    #     first_times = df_group.first()["time"]
    #     max_first = max(first_times)
    #     min_first = min(first_times)
    #     mixtimes.append(max_first - min_first)
    #     df_sub = df[df['time'] > max_first]
    #     df_group = df_sub.groupby('reactantA')

    # #return mixtimes
    # print(mixtimes)

    df_chunker = pd.read_csv(path,delim_whitespace=True,header=None,names=(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]),chunksize=100000)
    lookup = {}
    sampleTimes_i = list()
    mixTime=list()
    sampleTimes = list()
    i=0
    time_prev = 0
    print('test')
    for df in df_chunker:
        print(df.info(memory_usage='deep'))
        df = df[['time','reactantB','reactantA']]
        if i==0:
            df = df[df['time'] > 1e-7]  #Drop first 100 nanoseconds due to overlap of spheres at startup causing increased rxns
        #df = df[df['reactantA']==1]
        df = df.sort_values(by=['time','reactantA'])
        for index, row in df.iterrows():
            reacA_i = row["reactantA"]
            time_i = row['time']
            if (reacA_i not in lookup):
                lookup[reacA_i] = [time_i]
                sampleTimes_i.append(time_i-time_prev)
                time_prev = time_i

            if len(lookup)==42:
                sampleTimes.append(np.array(sampleTimes_i))
                mixTime.append((max(lookup.values()))[0]-min(lookup.values())[0])
                lookup = {}
                sampleTimes_i=list()
        i+=1
    return mixTime,sampleTimes

def discoveryTime(path):

    df_chunker = pd.read_csv(path,delim_whitespace=True,header=None,names=(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]),chunksize=100000)
    lookup = {}
    mixTime=list()
    sampleTimes = list()
    i=0
    time_prev = 0

    for df in df_chunker:
        print(df.info(memory_usage='deep'))
        df = df[['time','reactantA','reactantB']]

        reacA_rand = np.random.randint(df['reactantA'].min(),df['reactantA'].max()+1)
        reacB_rand = np.random.randint(df['reactantB'].min(),df['reactantB'].max()+1)
        print(reacA_rand," ",reacB_rand)

        df = df.sort_values(by=['time','reactantA','reactantB'])
        for index, row in df.iterrows():
            reacA_i = row["reactantA"]
            reacB_i = row["reactantB"]
            time_i = row['time']
            if (reacA_i==reacA_rand and reacB_i == reacB_rand):
                if(len(sampleTimes)==0):
                    sampleTimes.append(time_i)
                else:
                    sampleTimes.append(time_i-sampleTimes[-1])

    return sampleTimes

    #def processOutput(path):
     #   df_chunker = pd.read_csv(path,delimiter=" ",header=None,names=(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]),chunksize=500000)
      #  for df in df_chunker:


def collisionPickleAggregator(datapath, expts):
    """Aggregates multiple pickle files that each contain an array returned by totalCollision assessed on respective Smoldyn simulation output files
    
    Arguments:
        datapath {[type]} -- [description]
        expts {[]} -- A list of tuples. Each list contains the range of experiments that should be averaged across. For example,
        [(0,3),(3,6),(6,9),(9,12),(12,15)] means to calculate the average collisions between expts0,1,and2; then calculate the average collisions
        btwn expts3,4,5,...and so on. Then, a list of average collisions is returned for each tuple range provided (so, in the example, a list of 
        5 average collision values would be returned)
        
    
    Returns:
        [List] -- a list of average collisions is returned for each tuple range provided (so, in the example, a list of 
        5 average collision values would be returned)
    """
    collision_count=list()
    avg_coll_count = list()
    for expt_i in expts:
        data_arr_j=list()
        count_arr_j=list()
        for j in range(expt_i[0],expt_i[1]):
            try:
                collision_expt_path =glob.glob(datapath+'/analysis/expt-'+str(j)+'-*')[0]
                with open(collision_expt_path, 'rb') as f:
                    data_i = pkl.load(f)
                    count_arr_i = data_i[2]
                data_arr_j.append(data_i)
                count_arr_j.append(count_arr_i)
            except:
                print("Missing experiment")
        avg_coll_count.append(np.average(count_arr_j))
        collision_count.append(data_arr_j)
    #print(avg_coll_count)
    return avg_coll_count,collision_count

def mixTimePickleAggregator(datapath, expts,check_hittimes=False):
    mixTimes = list()
    hitTimes = list()
    for expt_i in expts:
        data_arr_j = list()
        hittimes_arr_j = list()
        for j in range(expt_i[0],expt_i[1]):
            try:
                expt_path = glob.glob(datapath+'/analysis/expt-'+str(j)+'-*')[0]
                with open(expt_path,'rb') as f:
                    data = pkl.load(f)
                    if check_hittimes:
                        data = data[0]
                    data_arr_j.append(np.average(data))
                    #print(data)
                #print(str(j))
            except:
                print("Missing experiment")
        mixTimes.append(np.average(data_arr_j))
    return mixTimes

def hitTimePickleAggregator(datapath,expts):
    hitTimes = list()
    for j in range(expts[0],expts[1]):
        try:
            expt_path = glob.glob(datapath+'/analysis/expt-'+str(j)+'-*')[0]
            with open(expt_path,'rb') as f:
                data = pkl.load(f)
                hitTimes_j = data[1]
                hitTimes.append([sum(hitTimes_onemix) for hitTimes_onemix in hitTimes_j])
        except:
            print("Missing experiment")
    return [i for hitTimes_i in hitTimes for i in hitTimes_i]

def computeTransportRxnTimes(path,simtime, num_rib,expt_start,expt_end,avg=False,scaling=1):
    """Calculates transport (how long particular tRNA unbound) and 
    reaction times (how long particular tRNA bound) from simulations
    
    Arguments:
        path {[type]} -- String to output folder
        simtime {[type]} -- Length of time over which to 
        num_rib {[type]} -- [description]
        expt_start {[type]} -- [description]
        expt_end {[type]} -- [description]
    
    Keyword Arguments:
        avg {bool} -- [description] (default: {False})
    
    Returns:
        [type] -- [description]
    """
    df_outputs = pd.read_csv(path+"outputReactionsList.txt",sep=" ",header=None) #Add batch processing here potentially
    transport_time = list()
    reaction_time = list()
    search_time = list()
    success_incorp = list()
    rxn17_tot = list()
    rxn21_tot = list()
    ribosome_reaction_time = list()
    print("Computing...")
    for expt_num, row in df_outputs.iterrows():
        succincorp_count = 0
        rxn17_count = 0
        rxn21_count = 0
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                my_cols=["time","rxn","x","y","z","reactantA","productA","productB","productC"]
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols,dtype={'reactantA':str,'productA':str,'productB':str,'productC':str})

                df=df.loc[df['rxn'].isin(["rxn17","rxn18","rxn19","rxn20","rxn21","rxn22","rxn23","rxn24","rxn26"])]
                df=df.loc[df['time']<simtime]

                ##Gets the id of which cognate tRNA succesfully bound to ribosomes (needed in cases where more than one cognate tRNA in voxel)
                df_succ_tRNA_id = int(df.loc[df['rxn'] == 'rxn18']['reactantA'].values[0].split('.')[0])
                df_succ_ribosome_id = int(df.loc[df['rxn'] == 'rxn18']['reactantA'].values[0].split('.')[1])

                df_rib = df[df['rxn'].isin(["rxn17","rxn18","rxn23","rxn24"])]
                df=df[df['reactantA'].apply(str).str.split('.').str[0].apply(int)==df_succ_tRNA_id]

                df=df[['time','rxn']]
                df_rib = df_rib[['time','rxn']]

                ## Calculate elong time from tracking succesful ribosome
                rib_reaction_time_i = list()
                rib_unbound_time_i = list()
                i=-1
                for _,row in df_rib.iterrows():
                    i+=1
                    if(row['rxn']=='rxn23'):
                        rib_reaction_time_i.append(float(df_rib.iloc[[i+1]]['time'])-row['time'])
                    if(row['rxn']=='rxn24'):
                        rib_unbound_time_i.append(float(df_rib.iloc[[i+1]]['time'])-row['time'])
                    if(row['rxn']=='rxn17'):
                        if(i==0):
                            rib_unbound_time_i.append(float(row['time']))
                        rib_reaction_time_i.append(float(df_rib.iloc[[i+1]]['time'])-row['time'])
                #print(np.sum(rib_reaction_time_i),'\n',np.sum(rib_unbound_time_i))

                transport_time_i = list()
                reaction_time_i = list()
                i=-1
                single_RxnTime = list() #Created to aggregate transport time between unsuccesful rxns into those btwn only succesful rxns
                single_TransportTime = list() #Created to aggregate transport time between unsuccesful rxns into those btwn only succesful rxns
                for _, row in df.iterrows():
                    i+=1
                    if(row["rxn"]=='rxn20'):
                        break
                    ### If the rxn is the cognate tRNA binding to a ribosome (can be a cognate or non-cognate binding reaction)
                    if((row["rxn"]=='rxn17' or row["rxn"]=='rxn21' or row["rxn"]=='rxn26')): #and succincorp_count<num_rib):
                        if(i>0):
                            ## Compute the time between the binding and when the tRNA was last let free
                            single_TransportTime.append(row['time']-float(df.iloc[[i-1]]['time']))
                        else:
                            single_TransportTime.append(row['time'])
                        if(row["rxn"]=='rxn17'):
                            rxn17_count+=1
                        elif (row["rxn"]=='rxn21'):
                            rxn21_count+=1

                    ### If the rxn is after binding between tRNA-ribosome, include as a reaction_time
                    if((row['rxn']=='rxn22' or row['rxn']=='rxn19')):# and succincorp_count<num_rib): #Ignore rxn18 because add that on separately
                        single_RxnTime.append(row['time']-float(df.iloc[[i-1]]['time']))

                    ### If the reaction is the binding of the cognate tRNA to the matching cognate ribosome 
                    #[note, this does not include the time for succesful incorp, but does include cognate tRNA unbinding time from cognate ribosome]
                    #Thus, we capture reaction time and transport time between cognate tRNA - cognate ribosome initial binding events
                    if(row['rxn']=='rxn17' or row['rxn']=='rxn26'):
                        succincorp_count+=1
                        transport_time_i.append(sum(single_TransportTime))
                        reaction_time_i.append(sum(single_RxnTime))
                        rxn17_tot.append(rxn17_count)
                        rxn21_tot.append(rxn21_count)
                        single_TransportTime = list()
                        single_RxnTime = list()

                #print(reaction_time_i)
                #if(succincorp_count<num_rib and avg==True):
                 #   transport_time_i = transport_time_i[:-1] #drops the last transport time if there wasn't a reaction recorded afterwards (else last transport time would be too short)
                #Need to scale both transport and reaction time: since all reactions are set to happen a scaling factor shorter,
                #the time the cognate tRNA spends in transport also reduces by 10x since ribosomes are available to be bound quicker.
                #i.e., if ribosomes are all bound by othe non-cognates for 10x longer, the cognate tRNA spends 10x longer in transport time.
                #transport_time.append([np.sum(transport_time_i)])
                transport_time.append([np.sum(rib_reaction_time_i)*scaling+np.sum(rib_unbound_time_i) - np.sum(reaction_time_i)*scaling])
                reaction_time.append([np.sum(reaction_time_i)*scaling])
                #search_time.append([np.sum(transport_time_i)+np.sum(reaction_time_i)*scaling])
                search_time.append([np.sum(rib_reaction_time_i)*scaling+np.sum(rib_unbound_time_i)])
                success_incorp.append([np.sum(succincorp_count)])

            except:
                print("missing expt")
                print(expt_num)

    return transport_time, reaction_time, success_incorp,rxn17_tot,rxn21_tot, search_time

def cognateDistrib(ptRNA,pCodon):

    ptRNA = np.divide(ptRNA,sum(ptRNA))
    pCodon= np.divide(pCodon, sum(pCodon))

    tRNA_tags = ["Ala1B", "Ala2", "Arg2", "Arg3", "Arg4", "Arg5", "Asn", "Asp1", "Cys", "Gln1", "Gln2", \
    "Glu2", "Gly2", "Gly3", "His", "Ile1", "Leu1", "Leu2", "Leu3", "Leu4", "Leu5", "Lys", \
    "Met_m", "Phe", "Pro1", "Pro2", "Pro3", "Sel_Cys", "Ser1", "Ser2", "Ser3", "Ser5", "Thr1", \
    "Thr2", "Thr3", "Thr4", "Trp", "Tyr1pTyr2", "Val1", "Val2ApB"]

    ptRNA_dict = dict(zip(tRNA_tags, ptRNA))
    
    codonLabels = pd.read_excel('codonValues.xlsx',header=None)[5]
    pcodon_dict = dict(zip(codonLabels,pCodon))

    #Note AUA does not have an assigned tRNA
    codon_dict={'GGG': ['Gly2'], 'GGA': ['Gly2'], 'GGU': ['Gly3'], 'GGC': ['Gly3'], \
    'GAG': ['Glu2'], 'GAA': ['Glu2'], 'GAU': ['Asp1'], 'GAC': ['Asp1'], \
    'GUG': ['Val1'], 'GUA': ['Val1'], 'GUU': ['Val1','Val2ApB'], \
    'GUC': ['Val2ApB'], 'GCG': ['Ala1B'], 'GCA': ['Ala1B'], 'GCU': ['Ala1B'], \
    'GCC': ['Ala2'], 'AGG': ['Arg5'], 'AGA': ['Arg4'], 'AGU': ['Ser3'], \
    'AGC': ['Ser3'], 'AAG': ['Lys'], 'AAA': ['Lys'], 'AAU': ['Asn'], \
    'AAC': ['Asn'], 'AUG': ['Met_m'], 'AUA': [], 'AUU': ['Ile1'], \
    'AUC': ['Ile1'], 'ACG': ['Thr2','Thr4'], 'ACA': ['Thr4'], \
    'ACU': ['Thr1','Thr4','Thr3'], 'ACC': ['Thr3','Thr1'], \
    'UGG': ['Trp'], 'UGA': ['Sel_Cys'], 'UGU': ['Cys'], 'UGC': ['Cys'], \
    'UAU': ['Tyr1pTyr2'], 'UAC': ['Tyr1pTyr2'], 'UUG': ['Leu5','Leu4'], \
    'UUA': ['Leu5'], 'UUU': ['Phe'], 'UUC': ['Phe'], 'UCG': ['Ser1','Ser2'], \
    'UCA': ['Ser1'], 'UCU': ['Ser5','Ser1'], 'UCC': ['Ser5'], 'CGG': ['Arg3'], \
    'CGA': ['Arg2'], 'CGU': ['Arg2'], 'CGC': ['Arg2'], 'CAG': ['Gln2'], \
    'CAA': ['Gln1'], 'CAU': ['His'], 'CAC': ['His'], 'CUG': ['Leu1','Leu3'], \
    'CUA': ['Leu3'], 'CUU': ['Leu2'], 'CUC': ['Leu2'], 'CCG': ['Pro1','Pro3'], \
    'CCA': ['Pro3'], 'CCU': ['Pro2','Pro3'], 'CCC': ['Pro2']}

    cells = 1
    voxels = 100000
    time = 180
    tRNA_distrib_arr = list()
    codon_count = {}
    codon_time = {}
    codon_time_avg = {}
    codon_time_weighted_avg={}
    codon_count_hist = {}
    codon_count_hist_weighted_avg = np.zeros(42)
    p_codon_tRNA = {}

    np.random.seed(0)

    for key in codon_dict:
        codon_count[key] = []
        codon_time[key] = []
        codon_time_avg[key] = []
        codon_time_weighted_avg[key]=[]
        codon_count_hist[key]=[]
        p_codon_tRNA[key] = []

    # Construct dictionary that assigns probability of all tRNA specific to a certain codon
    # to that codon (p_codon_tRNA)
    for codon in codon_dict:
        p_codon_tRNA_i = 0
        for tRNA in codon_dict[codon]:
            p_codon_tRNA_i += ptRNA_dict[tRNA]
        p_codon_tRNA[codon].append(p_codon_tRNA_i)

    for cell in range(cells):
        # Generate distribution for cognate tRNA count for each codon
        for i in range(voxels):

            #Choose 1 random codon for tranlsation voxel (weighted by codon probabilities), and identify cognate and non cognate ternary complexes
            codon_vox = np.random.choice(codonLabels, 1)
            cognatetRNA = codon_dict[codon_vox[0]]
            noncognatetRNA = [tRNA for tRNA in tRNA_tags if tRNA not in codon_dict[codon_vox[0]]]

            ##Create biased tRNA distribution, if bias exists.
            #biased_ptRNA = ptRNA.copy()
            #for _,tRNA_i in enumerate(cognatetRNA):
            #    biased_ptRNA[tRNA_tags.index(tRNA_i)]=biased_ptRNA[tRNA_tags.index(tRNA_i)]*bias
            #for _,tRNA_i in enumerate(noncognatetRNA):
            #    biased_ptRNA[tRNA_tags.index(tRNA_i)]=biased_ptRNA[tRNA_tags.index(tRNA_i)]/bias
            #biased_ptRNA = biased_ptRNA/sum(biased_ptRNA)

            #Construct translation voxel (weighted by specific tRNA abundances and bias)
            tRNA_vox = list(np.random.choice(tRNA_tags,42,p=ptRNA))


            #Count how many cognate tRNA appeared in the translation unit (for given codon) and record in codon_count
            codon_count_i = 0
            for tRNA in cognatetRNA:
                codon_count_i += tRNA_vox.count(tRNA)
            codon_count[codon_vox[0]].append(codon_count_i)

        for codon in codon_count:
            #Generate histogram of cognate tRNA counts for each codon
            codon_count_hist[codon] = np.histogram(codon_count[codon], bins=np.arange(0,43))[0]/sum(np.histogram(codon_count[codon], bins=np.arange(0,43))[0])

            #Weight histogram by codon probabilities to generate weighted average histogram for all codon
            codon_count_hist_weighted_avg += codon_count_hist[codon]*pcodon_dict[codon]
        p_codon_count_hist_weighted_avg = codon_count_hist_weighted_avg
        #print(p_codon_count_hist_weighted_avg)
    return p_codon_count_hist_weighted_avg

def transportRxnCalc(gr, ptRNA, pCodon,bias=1):
    colors = ['darkblue','#D43F3A']
    gr_i_list = ['gr_1']
    phi_list = [0.13,0.22,0.30,0.36,0.39,0.42]
    markers = ['*','^']
    transport_phi = list()
    reaction_phi = list()
    search_phi = list()
    transport_std_phi =list()
    rxn_std_phi =list()
    search_std_phi =list()
    search_list = list()
    
    p_codon_count_hist_weighted_avg=cognateDistrib(ptRNA,pCodon)
    
    for j,gr_i in enumerate(gr_i_list):
        transport_vals_list = list()
        reaction_vals_list = list()
        search_vals_list = list()
        transport_var_list = list()
        rxn_var_list = list()
        search_var_list = list()
        
        #for range(1,7)
        for i in range(list(gr['gr_1'].keys())[0],list(gr['gr_1'].keys())[-1]+1):
            transport_vals = gr[gr_i][i].avg_transportT*1000/1608733*p_codon_count_hist_weighted_avg[i]#/(1-p_codon_count_hist_weighted_avg[0])
            rxn_vals = gr[gr_i][i].avg_rxnT*1000/1608733*p_codon_count_hist_weighted_avg[i]#/(1-p_codon_count_hist_weighted_avg[0])
            search_vals = gr[gr_i][i].avg_searchT*1000/1608733*p_codon_count_hist_weighted_avg[i]#/(1-p_codon_count_hist_weighted_avg[0])
            
            ##To scale variance correctly, need to multiply by square of the constant being multiplied to the mean
            transport_var = (gr[gr_i][i].std_transportT)**2*(1000/1608733*p_codon_count_hist_weighted_avg[i])**2#/(1-p_codon_count_hist_weighted_avg[0])
            rxn_var = (gr[gr_i][i].std_rxnT)**2*(1000/1608733*p_codon_count_hist_weighted_avg[i])**2#/(1-p_codon_count_hist_weighted_avg[0])
            search_var = (gr[gr_i][i].std_searchT)**2*(1000/1608733*p_codon_count_hist_weighted_avg[i])**2#/(1-p_codon_count_hist_weighted_avg[0])

            transport_vals_list.append(np.array(transport_vals))
            reaction_vals_list.append(np.array(rxn_vals))
            search_vals_list.append(np.array(search_vals))
            
            transport_var_list.append(np.array(transport_var))
            rxn_var_list.append(np.array(rxn_var))
            search_var_list.append(np.array(search_var))
            
            search_list.append(np.array(gr[gr_i][i].searchT)*1000/1608733)
            print('Unweighted search time (', str(i), ' cognate)', np.array(search_vals/p_codon_count_hist_weighted_avg[i]))
        transport_phi.append(np.sum(transport_vals_list))
        reaction_phi.append(np.sum(reaction_vals_list))
        search_phi.append(np.sum(search_vals_list))
        
        transport_std_phi.append(np.sqrt(np.sum(transport_var_list)))
        rxn_std_phi.append(np.sqrt(np.sum(rxn_var_list)))
        search_std_phi.append(np.sqrt(np.sum(search_var_list)))

    print("Transport time: ", transport_phi, " +/- ", transport_std_phi)
    print("Reaction time: ", reaction_phi, " +/- ", rxn_std_phi)
    print("Search time: ", search_phi, " +/- ", search_std_phi)
    
    return search_list,transport_phi, reaction_phi, search_phi, transport_std_phi,rxn_std_phi,search_std_phi


def eventbased_sim(rib_num=1,tRNA_cog=1,repeatAllowed=True,bias=1,repeatTracker=False):
    import numpy as np

    #arbitrarily pick rib_id = 0 as the matching ribosome
    #arbitrarily pick tRNA ids 0 to tRNA_cog as cognate tRNAs
    tRNA_id=np.arange(42)
    
    elong_times = list()
    cog_bind=False;
    sys_t=0
    rxns=0
    
    ### Create probability distribution for tRNA near matching ribosomes (bias for cognate ternary complexes)
    p_cogRib=[bias*1/42]*tRNA_cog
    p_cogRib=np.concatenate((p_cogRib,[1/42]*(42-tRNA_cog)))
    p_cogRib = p_cogRib/sum(p_cogRib)
    
    ### Create probability distribution for tRNA near non-matching ribosomes (anti-bias for cognate ternary complexes)
    p_noncogRib=[1/(42*bias)]*tRNA_cog 
    p_noncogRib=np.concatenate((p_noncogRib,[1/42]*(42-tRNA_cog)))
    p_noncogRib=p_noncogRib/sum(p_noncogRib)
    
    ## Randomly pick the tRNA to be bound to the matching ribosome from all possible tRNA.
    # Picking is biased based on p_cogRib
    tRNA_bound=np.random.choice(tRNA_id,1,replace=False,p=p_cogRib)
    tRNA_unbound = [tRNA for tRNA in tRNA_id if tRNA not in tRNA_bound]


    ##From the remaining unbound tRNA, pick tRNA for all other ribosomes (all of which are non-matching)
    # Picking is biased based on p_noncogRib
    if rib_num>1:
        tRNA_bound=np.concatenate((tRNA_bound,np.random.choice(tRNA_unbound,rib_num-1,replace=False,p=p_noncogRib[tRNA_unbound]/sum(p_noncogRib[tRNA_unbound]))))
        tRNA_unbound = [tRNA for tRNA in tRNA_id if tRNA not in tRNA_bound]


    ## For each ribosome, now with a reacting tRNA, pick an exponential random time until dissociation 
    #(assuming cognate ternary complex hasn't bound to matching ribosome)
    # Ribosome array index 0 is the cognate ribosome, which is bound for time react_time[0]
    k_r = 717
    react_time = np.random.exponential(1000/k_r,rib_num)

    ##Tracking reaction latencies for each ternary complex (i.e., total time each ternary complex spends bound). Transport latency is directly computed from total sim time.
    tRNA_reaction = np.zeros(42)
    tRNA_reaction[tRNA_bound] = react_time


    ## Dealing with the case of cognate tRNA binding to matching ribosome.
    # We account for the chance that the cognate tRNA unbinds from the matching ribosome
    k_f = 1475
    if tRNA_bound[0] in np.arange(tRNA_cog) and np.random.uniform(0,1)<k_f/(k_f+k_r):
        cog_bind=True
        sys_t+=tRNA_reaction[tRNA_bound[0]]
        return sys_t,rxns,tRNA_reaction[tRNA_bound[0]],sum(p_cogRib[0:tRNA_cog])

    reactionIDTracker = list()
    #### Loop while cognate tRNA isn't bound to cognate ribosome successfully
    while not cog_bind:

        ###Find next event (a tRNA unbinding from a ribosome) and jump the system to this time
        next_rib_time = min(react_time)
        next_rib = np.argmin(react_time)
        just_unbound_tRNA = tRNA_bound[next_rib]


        ##Adjust all pending reaction times by change in system time
        sys_t+= next_rib_time
        react_time = react_time - np.ones(rib_num)*next_rib_time
        

        ##Pick new tRNA to be bound to recently unbound ribosome, based on whether repeat reactions are allowed or not
        unbound_tRNA_repeattransient = np.concatenate((tRNA_unbound,[just_unbound_tRNA]))
        if repeatAllowed:
            if next_rib==0:
                next_tRNA = np.random.choice(unbound_tRNA_repeattransient,size=1,replace=False,p=p_cogRib[unbound_tRNA_repeattransient]/sum(p_cogRib[unbound_tRNA_repeattransient]))
            else:
                next_tRNA = np.random.choice(unbound_tRNA_repeattransient,size=1,replace=False,p=p_noncogRib[unbound_tRNA_repeattransient]/sum(p_noncogRib[unbound_tRNA_repeattransient]))
 
        else:
            if next_rib==0:
                next_tRNA = np.random.choice(tRNA_unbound,size=1,replace=False,p=p_cogRib[tRNA_unbound]/sum(p_cogRib[tRNA_unbound]))
            else:
                next_tRNA = np.random.choice(tRNA_unbound,size=1,replace=False,p=p_noncogRib[tRNA_unbound]/sum(p_noncogRib[tRNA_unbound]))

        tRNA_bound[next_rib] = next_tRNA
        tRNA_unbound = [tRNA for tRNA in tRNA_id if tRNA not in tRNA_bound]
        
        
        #Count number of times a ternary complex reacted with the matching ribosome
        if(next_rib==0):
            rxns+=1
            if(next_tRNA != 0):
                reactionIDTracker.append(next_tRNA[0])

        ## Check if newly bound ternary complex is the cognate bound to the matching ribosome, and if so, whether the reaction is successful 
        k_r = 717
        k_f= 1475
        if tRNA_bound[0] in np.arange(tRNA_cog) and next_rib==0:
            if np.random.uniform(0,1)<k_f/(k_f+k_r):
                rxnt = np.random.exponential(1000/k_f)
                sys_t+= rxnt
                tRNA_reaction[tRNA_bound[0]]+=rxnt
                if not repeatTracker:
                    return sys_t,rxns, tRNA_reaction[tRNA_bound[0]],sum(p_cogRib[0:tRNA_cog])
                elif len(reactionIDTracker)>1000000:
                    return sys_t,rxns, tRNA_reaction[tRNA_bound[0]],sum(p_cogRib[0:tRNA_cog]),reactionIDTracker

        ##Else, pick a mismatch reaction time for the newly bound tRNA
        rxnt = np.random.exponential(1000/k_r)
        react_time[next_rib] = rxnt
        tRNA_reaction[next_tRNA]+=rxnt

    #return sys_t,rxns, tRNA_reaction[tRNA_bound[0]]


def countIncorrectReactions(path,simtime, num_rib,expt_start,expt_end,avg=False,scaling=1):
    df_outputs = pd.read_csv(path+"outputReactionsList.txt",sep=" ",header=None) #Add batch processing here potentially

    rxn21_tot = list()
    print("test")
    for expt_num, row in df_outputs.iterrows():

        rxn21_count = 0
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                my_cols=["time","rxn","x","y","z","reactantA","productA","productB","productC"]
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols)
                df=df.loc[df['rxn'].isin(["rxn21"])]
                rxn21_count = df.shape[0]
                rxn21_tot.append(rxn21_count)

                #print(df.shape[0])

            except:
                print("missing expt")
                print(expt_num)
    #print(rxn21_tot)

    return np.average(rxn21_tot), np.std(rxn21_tot)


def countIncorrectRepeatReactions(path,simtime, num_rib,expt_start,expt_end,avg=False,scaling=1):
    df_outputs = pd.read_csv(path+"outputReactionsList.txt",sep=" ",header=None) #Add batch processing here potentially

    rxn21_tot = list()
    for expt_num, row in df_outputs.iterrows():
        rxn21_count = 0
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                #print(expt_num)
                my_cols=["time","rxn","x","y","z","reactantA","productA","productB","productC"]
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols)
                df=df.loc[df['rxn'].isin(["rxn22"])]
                #print(df)

                df=df.loc[:,['time','productA','productB']]
                #pd.set_option('display.max_rows', None)
                df = df.sort_values(['productA','time'], ascending=[True, True])
                #print(df)

                reactant = '-1'
                repeat=0
                first = True
                for _, row in df.iterrows():
                    if row['time']<simtime:
                        #print("# repeat ", repeat, " molecules ", reactant, " and ", row["productB"])
                        if(row["productB"]==reactant):
                            repeat+=1

                        else:
                            if first==False:
                                rxn21_tot.append(repeat)
                            repeat=0
                            reactant = row["productB"]
                            first=False

                #print(df.shape[0])
                if repeat != 0:
                    rxn21_tot.append(repeat)

            except:
                print("missing expt")
                print(expt_num)
    #print(rxn21_tot)
    return np.average(rxn21_tot), np.std(rxn21_tot)/np.sqrt(len(rxn21_tot)-1)

def countIncorrectRepeatCollisions(path,expt_start,expt_end,equalRibosomes=False,ts_equillibrate=0, avg=False,scaling=1):
    df_outputs = pd.read_csv(path+"outputReactionsList.txt",sep=" ",header=None) #Add batch processing here potentially

    rxn14_tot = list()
    print("test")
    for expt_num, row in df_outputs.iterrows():
        rxn14_count = 0
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                my_cols=["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols)
                df=df[['time','reactantA','reactantB']]

                df=df.loc[df['time']>ts_equillibrate]

                if(equalRibosomes):
                    df=df.loc[df['reactantA'].isin(["1","2","3","4"])]

                df=df.sort_values(['reactantA', 'time'])
                reactantA = '-1'
                reactantB = '-1'
                repeat=0
                for _, row in df.iterrows():
                    if(row["reactantA"]==reactantA and row["reactantB"]==reactantB):
                        repeat+=1
                    else:
                        rxn14_tot.append(repeat)
                        repeat=0
                        reactantA = row["reactantA"]
                        reactantB= row["reactantB"]
            except:
                print("missing expt")
                print(expt_num)

    return np.average(rxn14_tot), np.std(rxn14_tot)
class CellLatencies:
    def __init__ (self,TransportRxnTimesarr,bootstrap=True):
        self.transportT = [i for trans_i in TransportRxnTimesarr[0] for i in trans_i]
        self.rxnT = [i for reac_i in TransportRxnTimesarr[1] for i in reac_i]
        self.incorrRxn = TransportRxnTimesarr[4]
        self.searchT = [i for search_i in TransportRxnTimesarr[5] for i in search_i]
       
        self.avg_transportT = np.average(self.transportT)     
        self.avg_rxnT = np.average(self.rxnT)   
        self.avg_searchT = np.average(self.searchT)    

        self.std_transportT = np.std(self.transportT)/np.sqrt(len(self.transportT)-1)
        self.std_searchT = np.std(self.searchT)/np.sqrt(len(self.searchT)-1)
        self.std_rxnT = np.std(self.rxnT)/np.sqrt(len(self.rxnT)-1)


def getTotalSuccessIncorpTime(path,expt_start,expt_end):
    df_outputs = pd.read_csv(path+"outputReactionsList.txt",sep=" ",header=None) #Add batch processing here potentially
    success_incorp = list()
    for expt_num, row in df_outputs.iterrows():
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                my_cols=["time","rxn","x","y","z","reactantA","productA","productB","productC"]
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols)
                df=df.loc[df['rxn'].isin(["rxn27","rxn18"])]
                success_incorp.append(df['time'].iloc[0])
                df=df.loc[df['rxn'].isin(["rxn27","rxn18"])]
            except:
                print("missing expt")
                print(expt_num)
    return success_incorp

def getTotalSuccessIncorpTimeModified(path,expt_start,expt_end,scaling=1):
    df_outputs = pd.read_csv(path+"outputReactionsList.txt",sep=" ",header=None) #Add batch processing here potentially
    success_incorp = list()
    for expt_num, row in df_outputs.iterrows():
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                incorrtime_tot_scaled = 0
                my_cols=["time","rxn","x","y","z","reactantA","productA","productB","productC"]
                df = pd.read_csv(path+row[0],delimiter=" ",header=None, names=my_cols)
                df_corr=df.loc[df['rxn'].isin(["rxn27","rxn18"])]
                df_incorr=df.loc[df['rxn'].isin(["rxn24","rxn23"])]
                prevrow=0
                for _, row in df_incorr.iterrows():
                    incorrtime_tot_scaled+=(row['time']-prevrow)*(scaling-1)
                    prevrow = row['time']
                success_incorp.append(df_corr['time'].iloc[0]+incorrtime_tot_scaled)
            except:
                print("missing expt")
                print(expt_num)
    return success_incorp

def countRibosomeCollisions(df,tRNAIDList,ribosomeIDList):
    """Counts the number of collisions that a single tRNA has with each ribosome from 
    a group of ribosomes provided (in a given Smoldyn reaction_log dataframe)
    
    Args:
        df (dataframe): dataframe containing Smoldyn reaction_log data
        tRNAid (int): id of tRNA which to 
        ribosomeIDList (list): list of ribosome IDs from which to count
    
    Returns:
        tRNACollisionCount_r (np array): Array containing number of collisions between a given tRNA
            and all ribosomes in ribosomeIDList
    """
    #Sort the data based on ascending ribosome ID ('reactantB') and reaction timestamp ('time')
    df=df.sort_values(['reactantB','time'], ascending=[True,True])

    # Create two arrays the length or # ribosome IDs to check collisions with
    tRNACollisionCount_rt=np.zeros([len(ribosomeIDList),len(tRNAIDList)])
    print("Computing tRNA collision count [rib,tRNA]: "+str(tRNACollisionCount_rt.shape))
    #Iterate through the sorted dataframe reaction by reaction (row by row)
    df_r = df.loc[df['reactantB'].isin(ribosomeIDList)]
    df_r=df_r.sort_values(['reactantB','time'], ascending=[True,True])

    prevtRNAID = -1;
    prevRibID = -1
    for i, rxn_i in df_r.iterrows():
        #Iterate through ribosomes being tracked, and for the ribosome that the tRNA collided with for the given rxn_i: 
        #1) increment collision count
        
        ribosome_i = rxn_i["reactantB"]
        tRNA_i = rxn_i["reactantA"]
        if(tRNA_i in tRNAIDList and tRNA_i != prevtRNAID and ribosome_i == prevRibID):
            tRNACollisionCount_rt[int(np.where(ribosomeIDList==ribosome_i)[0]),int(np.where(tRNAIDList==tRNA_i)[0])]+=1
        prevtRNAID = tRNA_i
        prevRibID = ribosome_i


    #print(tRNACollisionCount_rt)
    return tRNACollisionCount_rt

def countIncorrectRibosomeCollisions(df, tRNA_IDList, ribosome_IDList, tRNAInclusionList=np.array([])):
    """Creates a list for each tRNA and ribosome pair possible (tRNA_t and ribosome_r)
    of the # of time other tRNAs collided with the ribosome_r in between collisions of 
    the specified tRNA_t and ribosome_r (in a given Smoldyn reaction_log dataframe).
    
    
    Args:
        df (dataframe): dataframe containing Smoldyn reaction_log data
        tRNA_IDList (TYPE): List of tRNA IDs for which to check collisions 
        ribosome_IDList (TYPE): List of ribosome IDs for which to check collisions
    
    Returns:
        IncorrectCollisions_tr (List of Lists of Lists; rank 3 tensor): A list containing a list
        of ribosomes for each tRNAs. Each ribosome has a list that records in time order 
        incorrect collision number between each correct collision (between the ribosome and 
        corresponding tRNA parents). 
        The nested lists/tensor is ordered [trNAid, ribosomeid, collisionGapNumber] = # of incorrect collisions.
    """

    #Sort the data based on ascending ribosome ID ('reactantB') and reaction timestamp ('time')
    df=df.sort_values(['reactantB','time'], ascending=[True,True])
    IncorrectNumColMatrix_rt=np.zeros([len(ribosome_IDList),len(tRNA_IDList)])

    #Create a list of lists of lists (rank 3) [tRNAid, ribosomeid, collisionGapNumber]
    IncorrectCollisions_rt = list()
    for r in range(len(ribosome_IDList)):
        IncorrectCollisions_rt.append(list())
        for t in range(len(tRNA_IDList)):
            IncorrectCollisions_rt[r].append(list())
    print("Initial ribosome x tRNA x collisionGapNumber has shape:", np.array(IncorrectCollisions_rt).shape)

    if tRNAInclusionList.shape[0] == 0:
        tRNAInclusionList = np.arange(df["reactantA"].min(),df["reactantA"].max()+1)

    #Create a sub-dataframe df_r for each ribosome and iterate through each one
    for r_index, ribosomeID in enumerate(ribosome_IDList):
        #print("Currently processing ribosome #",r_index)
        df_r = df.loc[df['reactantB']==ribosomeID]
        prevtRNAID=-1;
        #Iterate through each ribosome sub dataframe
        for i, rxn_i in df_r.iterrows():   

            #Check to ensure the reactant is being considered as a tRNA & Check to see if the reactant is a repeat reactant, in which case ignore. 
            # If reactant is previous reactant then keeping prev rxn var same is ok. If reactantA not on tRNA list, then keeping prev rxn var same also ok.
            if rxn_i["reactantA"] in tRNAInclusionList: #and rxn_i["reactantA"]!=prevtRNAID:              
                for t_index, tRNAID in enumerate(tRNA_IDList):    #For each reaction, iterate through each tRNA. 
                    #Increment the incorrect collision count for each tRNA that wasn't involved 
                    #in the reaction (IncorrectNumColMatrix_tr). 

                    if rxn_i["reactantA"]!=tRNAID: #and (tRNAInclusionList.size==1 or rxn_i["reactantA"] in tRNAInclusionList):
                        IncorrectNumColMatrix_rt[r_index, t_index]+=1

                    #For the tRNA_t that was involved in the reaction, save the total other tRNA-ribosome_r 
                    #collisions that occured in between this reaction and the previous reaction with tRNA_t
                    #and ribosome_r in IncorrectCollisions_tr, and then reset the incorrect collision count
                    #(for tRNA_t-ribosome_r) back to 0.

                    elif rxn_i["reactantA"]==tRNAID:
                        IncorrectCollisions_rt[r_index][t_index].append(IncorrectNumColMatrix_rt[r_index, t_index])
                        IncorrectNumColMatrix_rt[r_index, t_index] = 0
                
                prevtRNAID = rxn_i["reactantA"]

    return IncorrectCollisions_rt


def timeSplitter(df, start_time=0, time_interval=0.01, scale="linear",logscalestart=-4):
    """Splits a given Smoldyn reaction_log dataframe into a list of dataframes each with reactions
    that occured between given timestamps. 
    
    Args:
        df (dataframe): dataframe containing Smoldyn reaction_log data. 
        start_time (int, optional): Start time at which to begin splitting reaction data. Default=0
        time_interval (float, optional): Time intervals in which to split reaction data. Default=0.01
        scale (str, optional): "linear" or "log". Log divides by powers of 10 (e.g., 10^-3,10^-2,...,10^2). Default="linear"
        logscalestart (TYPE, optional): if "log" scale selected, the ten power to start the log scale. Default=-3.
    
    Returns:
        timesplitdf_list: A list of dataframes each with reactions from specified time range. 
        In asending order of time frames.
    """

    #Sort overall reaction_log dataframe by ascending time 
    df=df.sort_values(['time'], ascending=[True])
    end_time = df.iloc[df.shape[0]-1]['time']

    #Create array of sampling times based on linear vs. log:
    if scale=="linear":
        #Time interval is added to end_time since np.arange doesn't take into account last interval
        time_arr = np.arange(start_time,end_time+time_interval,time_interval)
    elif scale=="log":
        #Logspace from the start until log10 rounded up end_time. Final param is # of intervals.
        time_arr = np.logspace(logscalestart,math.ceil(np.log10(end_time)),1+abs(logscalestart)+math.ceil(np.log10(end_time)))
    
    #Split up (cut) and group (groupby) the dataframe by the times in time_arr ("time" has timestamp)
    timesplitdf = df.groupby(pd.cut(df["time"],time_arr))

    #Create an ordered list of intervals (the interval is a key to the respective dataframe of reactions)
    intervalkeys = [interval for interval, timesplitdf_i in timesplitdf]

    #Add the time interval organized dataframes of reactions into a list to return 
    timesplitdf_list = list()
    for key in intervalkeys:
        timesplitdf_list.append(timesplitdf.get_group(key))

    return timesplitdf_list


def analyze(path, countRibosomeCollisionsMethod=True, countIncorrectRibosomeCollisionsMethod=True,tRNA_range=-1,rib_range=-1):
    df= readSimData(path)
    if(tRNA_range==-1):
        tRNA_range_arr=np.arange(df["reactantA"].min(),df["reactantA"].max()+1)
    if(rib_range==-1):
        rib_range_arr=np.arange(df["reactantB"].min(),df["reactantB"].max()+1)
    tRNACollisionCount_rt=countRibosomeCollisions(df, tRNA_range_arr,rib_range_arr)
    incorrectCollisions_rt=countIncorrectRibosomeCollisions(df, tRNA_range_arr,rib_range_arr)
    pkl.dump([tRNACollisionCount_rt,incorrectCollisions_rt],open(path[:-4]+".p","wb"))

#how do the 2 most "different" tRNAs (across histogram for all 3 ribosomes) -- create a calculation
#algorithm for this, quantitatively differ/differ when visualized for the 2 diff ribosomes?






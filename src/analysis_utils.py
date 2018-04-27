import pandas as pd
import numpy as np
import sys
import math
import pickle as pkl


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
    df = pd.read_csv(path,sep=" ")
    df.columns=["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]

    return df

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
        timeavg_r (np array): Array containing the average time stamp at which a given tRNA collided
            with all ribosomes in ribosomeIDList
    """
    #Sort the data based on ascending ribosome ID ('reactantB') and reaction timestamp ('time')
    df=df.sort_values(['reactantB','time'], ascending=[True,True])

    # Create two arrays the length or # ribosome IDs to check collisions with
    tRNACollisionCount_rt=np.zeros([len(ribosomeIDList),len(tRNAIDList)])
    print("Computing tRNA collision count [rib,tRNA]: "+str(tRNACollisionCount_rt.shape))
    #Iterate through the sorted dataframe reaction by reaction (row by row)
    for i, rxn_i in df.iterrows():
        #Iterate through ribosomes being tracked, and for the ribosome that the tRNA collided with for the given rxn_i: 
        #1) increment collision count 2) add the timestamp at which the reaction occured to the growing sum of reaction 
        #timestamps for that ribosome
        ribosome_i = rxn_i["reactantB"]
        tRNA_i = rxn_i["reactantA"]
        if tRNA_i in tRNAIDList and ribosome_i in ribosomeIDList:
            tRNACollisionCount_rt[int(np.where(ribosomeIDList==ribosome_i)[0]),int(np.where(tRNAIDList==tRNA_i)[0])]+=1

    #print(tRNACollisionCount_rt)
    return tRNACollisionCount_rt

def countIncorrectRibosomeCollisions(df, tRNA_IDList, ribosome_IDList):
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
    #Create a sub-dataframe df_r for each ribosome and iterate through each one
    for r_index, ribosomeID in enumerate(ribosome_IDList):
        #print("Currently processing ribosome #",r_index)
        df_r = df.loc[df['reactantB']==ribosomeID]

        #Iterate through each ribosome sub dataframe
        for i, rxn_i in df_r.iterrows():   

            #For each reaction, iterate through each tRNA. 
            for t_index, tRNAID in enumerate(tRNA_IDList):
                #Increment the incorrect collision count for each tRNA that wasn't involved 
                #in the reaction (IncorrectNumColMatrix_tr). 

                if rxn_i["reactantA"]!=tRNAID:
                    IncorrectNumColMatrix_rt[r_index, t_index]+=1

                #For the tRNA_t that was involved in the reaction, save the total other tRNA-ribosome_r 
                #collisions that occured in between this reaction and the previous reaction with tRNA_t
                #and ribosome_r in IncorrectCollisions_tr, and then reset the incorrect collision count
                #(for tRNA_t-ribosome_r) back to 0.

                elif rxn_i["reactantA"]==tRNAID:
                    IncorrectCollisions_rt[r_index][t_index].append(IncorrectNumColMatrix_rt[r_index, t_index])
                    IncorrectNumColMatrix_rt[r_index, t_index] = 0

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






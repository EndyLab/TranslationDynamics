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
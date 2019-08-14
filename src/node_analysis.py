"""
Created by Akshay Maheshwari
09/14/2018

Computes individual subexperiment analyses on a server (Map part of MapReduce)
"""

import glob
import os
import pickle as pkl
import numpy as np
import pandas as pd
from analysis_utils import *

data_path =glob.glob('./translation/data/*Reaction*')[0]
print("MY DIR: ", os.getcwd())
if not os.path.exists('./translation/data/analysis'):
    os.mkdir('./translation/data/analysis/')

#reaction_data = totalCollisions(data_path)
#path='./translation/data/analysis/'+os.path.basename(data_path).split('.')[0]+'_collision_count.pkl'
#print("datapath",path)
#pkl.dump(reaction_data,open(path,"wb"))


mixtime_data = mixTime(data_path)
mixTimePath='./translation/data/analysis/'+os.path.basename(data_path).split('.')[0]+'_mixtime.pkl'
pkl.dump(mixtime_data,open(mixTimePath,"wb"))

os.mkdir('./translation/data/pckldone/')

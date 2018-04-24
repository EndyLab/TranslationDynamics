"""
Created by Akshay Maheshwari
09/05/2017

Produces smoldyn parameter specification files that sweep parameters in a specified way.
"""
def setup():
	import os
	import datetime
	import numpy as np

	###### DEFINE VARIABLES #######
	exptNum = 13

	#Cube side length (µm)
	_side_len_ = 0.085 

	#Molecule radius (µm)
	_tRNAEfTu_RAD_ = 0.0075
	_ribosome_RAD_ = 0.012 
	_aa_RAD_ = 0.00031 

	#Diffusion coefficient, µm^2/s
	_D_tRNAEfTu_ = 43 
	_D_ribosome_ = 0.04
	_D_tRNAsynth_ = 132
	_D_aa_ = 1061

	#Number of molecules
	_tRNAEfTuNum_=47 
	_ribosomeNum_=7
	_tRNAsynthNum_=8
	_aaNum_=863

	#Simulation time details (seconds)
	_time_start_ = 0 
	_time_step_ = 1e-9 #Want RMSD = sqrt(6tD) << smallest molecule radius
	_time_stop_ = 0.1

	#Volume dimensions and simulation seed
	 dim 3
	_random_seed_ = 1000


	######## BEGIN WRITING EXPERIMENT FILE ##########
	_exptname_ = "expt"+exptNum+"_"_tRNAEfTuNum_+"tRNAEfTu"+_ribosomeNum_+"ribosome"+
	_tRNAsynthNum_+"tRNAsynth"+_aaNum_+"aa_"+int(_side_len_*1000)"sidelength_"datetime.date.today().strftime('%Y%m%d')+"_smoldyn.txt"

	_reaction_log_ = "expt"+exptNum+"_"_tRNAEfTuNum_+"tRNAEfTu"+_ribosomeNum_+"ribosome"+
	_tRNAsynthNum_+"tRNAsynth"+_aaNum_+"aa_"+_side_len_"sidelength_"datetime.date.today().strftime('%Y%m%d')+ ".csv"

	expt = open("data/" + exptname,'w')

	expt.write("define _side_len_ " + str(_side_len_) + "\n")

	expt.write("variable _tRNAEfTu_RAD_ " + str(_mol1RAD_)+ "\n")
	expt.write("variable _ribosome_RAD_ " + str(_mol1Num_)+ "\n")
	expt.write("variable _tRNAsynth_RAD_ " + str(_Dc1_) + "\n")
	expt.write("variable _aa_RAD_ " + str(_mol2RAD_)+ "\n")


	expt.write("variable _mol2Num_ " + str(_mol2Num_)+ "\n")
	expt.write("define_global _mol2Position_ " + str(_mol2Position_) +"\n")
	expt.write("variable _Dc2_ " + str(_Dc2_) + "\n")

	expt.write("variable _ts_ " + str(_ts_)+ "\n")
	expt.write("variable _bins_ " + str(_bins_)+ "\n")

	expt.write("define_global _simtime_ " + str(_simtime_)+ "\n")
	#expt.write("define_global _simtimeTS_ " + str(_simtimeTS_)+ "\n")
	expt.write("define_global _outputSimtime_ " + "data/"+_outputSimtime_ +"\n")

	expt.write("define_global _molposTS_ " + str(_molposTS_) + "\n")
	expt.write("define_global _outputMolpos_ " + "data/"+_outputMolpos_)

	####### Write list of experiment and output
	exptList.write(exptname + "\n")
	outputSimtimeList.write(_outputSimtime_ + "\n")
	outputMolposList.write(_outputMolpos_ + "\n")


	expt_description.write("Sampling of "+ str(_mol2Num_) +"molecule position (molpos) in" + str(_mol2Num_)+" molecules (monodisperse)"+" \n")
	expt_description.write("Total simulation time: "+ str(_simtime_) + "s. ; Simulation time step: " + str(_ts_)+" s.")
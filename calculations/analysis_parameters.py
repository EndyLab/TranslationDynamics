from bisect import bisect_left
import numpy as np
import matplotlib.pyplot as plt

def takeClosest(myList, myNumber):
	"""
	Assumes myList is sorted. Returns closest value to myNumber.

	If two numbers are equally close, return the smallest number.
	"""
	pos = bisect_left(myList, myNumber)
	if pos == 0:
		return myList[0]
	if pos == len(myList):
		return myList[-1]
	before = myList[pos - 1]
	after = myList[pos]
	if after - myNumber < myNumber - before:
	   return after
	else:
	   return before

def f_rib(dbl_rate):
	"""
	
	Fits a first order polynomial to experimental data points describing how active ribosome abundance changes with growth rate,
	and returns the estimated abundance of ribosomes that should be expected for a given input growth rate.
	
	Arguments:
		dbl_rate {float} -- Input doubling time
	
	Returns:
		rib_i -- A float describing the number of expected active ribosomes for input doubling time
	"""
	rib_GrowthRate = [0.6,1.0,1.5,2.0,2.5,3.0]
	ribosomes = [8000,15000,26000,44000,61000,73000]
	activeRibosomes = [int(x*0.85) for x in ribosomes]
	ribPolyFit = np.polyfit(rib_GrowthRate,activeRibosomes,1)
	rib_i = dbl_rate*ribPolyFit[0]+ribPolyFit[1]
	
	return rib_i

def f_tern(dbl_rate):
	"""
	
	Fits a second order polynomial to experimental data points describing how ternary complex abundance changes with growth rate,
	and returns the estimated abundance of ternary complexes that should be expected for a given input growth rate.
	
	Arguments:
		dbl_rate {float} -- Input doubling time
	
	Returns:
		tern_i -- A float describing the number of expected # of ternary complexes in a cell for input doubling time
	"""
	tern_GrowthRate = np.array([0.4,0.7,1.07,1.6,2.5,3.0]+[0.4]*5)
	ternaryComplexes = np.array([48000,57000,83000,143000,323000,383000]+[48000]*5)
	tern_PolyFit = np.polyfit(tern_GrowthRate,ternaryComplexes,2)
	
	tern_i = dbl_rate**2*tern_PolyFit[0]+dbl_rate*tern_PolyFit[1]+tern_PolyFit[2]
	
	return tern_i

def f_mass(dbl_rate):
	"""
	
	Fits a second order polynomial to experimental data points describing how cell mass changes with growth rate,
	and returns the estimated cell mass that should be expected for a given input growth rate.
	
	Arguments:
		dbl_rate {float} -- Input doubling time
	
	Returns:
		mass_i -- A float describing the cell mass for input doubling time
	"""
	mass_GrowthRate = [0.6,1.0,1.5,2.0,2.5,3.0]
	mass = [159,257,370,512,607,636]
	mass_PolyFit = np.polyfit(mass_GrowthRate,mass,2)
	
	mass_i = dbl_rate**2*mass_PolyFit[0]+dbl_rate*mass_PolyFit[1]+mass_PolyFit[2]
	return mass_i

def f_vol(dbl_rate):
	"""
	
	Fits a second order polynomial to experimental data points describing how cell volume changes with growth rate,
	and returns the estimated cell volume that should be expected for a given input growth rate.
	
	Arguments:
		dbl_rate {float} -- Input doubling time
	
	Returns:
		vol_i -- A float describing the cell volume for input doubling time
	"""

	vol_GrowthRate = [0.25,0.42,0.56,0.58,0.68,0.71,0.87,1.81,1.85,2.15,2.3]
	vol = [1.14,1.44,1.74,1.26,1.11,1.38,1.44,2.15,2.34,2.46,2.4]
	vol_PolyFit = np.polyfit(vol_GrowthRate,vol,1)

	vol_i = dbl_rate*vol_PolyFit[0]+vol_PolyFit[1]
	return(vol_i)

def f_nuc(dbl_rate):
	"""
	
	Fits a second order polynomial to experimental data points describing how cell volume changes with growth rate,
	and returns the estimated cell volume that should be expected for a given input growth rate.
	
	Arguments:
		dbl_rate {float} -- Input doubling time
	
	Returns:
		vol_i -- A float describing the cell volume for input doubling time
	"""

	nuc_GrowthRate = [0.4,1.36,2.85]
	#nuc = [0.17,0.13,0.11]
	nuc = [0.17,0.13,0.11]
	nuc_PolyFit = np.polyfit(nuc_GrowthRate,nuc,1)

	nuc_i = dbl_rate*nuc_PolyFit[0]+nuc_PolyFit[1]
	return(nuc_i)


def calcParams(rib_num,tern_num,cell_mass,cell_vol,nuc_volfrac): 
	"""
	Transforms cell input parameters into cell dimensional/dimensionless paramters + into nucleoid-excluded voxel parameters. Presumably, parameters are 
	all from an equivalent growth rate, though this is not neccessary, and cell/voxel parameters can be  calculated for any set of input cell parameters.
	
	Arguments:
		rib_num {[float]} -- [Number of active ribosomes (i.e., mRNA bound) in a cell]
		tern_num {[float]} -- [Number of ternary complexes in a cell]
		cell_mass {[float]} -- [Cell mass]
		cell_vol {[float]} -- [Cell volume]
		nuc_volfrac {[float]} -- [Fraction of cell that is occupied by the nucleoid (i.e., volume that the active ribosomes cannot occupy)]
	
	Returns:
		[list, list] -- [cell parameters, voxel parameters]
	"""
	RIB_MASS= kD_to_fg(2300)
	TERN_MASS = kD_to_fg(69)
	RIB_RAD = 0.01305
	TERN_RAD = 0.0059
	CROWDER_RAD = 0.0020
	PROTEIN_DENSITY = 1.41 #g/cm^3
	CROWDER_MASS = ((4/3)*np.pi*(CROWDER_RAD**3))*10**-12*PROTEIN_DENSITY*10**15 #~56kD
	rib = Macromolecule(RIB_MASS, RIB_RAD,rib_num)
	tern= Macromolecule(TERN_MASS,TERN_RAD, tern_num)
	crowder = Macromolecule(CROWDER_MASS,CROWDER_RAD)
	cell_i = Cell(cell_mass,cell_vol,rib,tern,crowder,nuc_volfrac)
	vox_i = Voxel(42, cell_i)
	
	return cell_i.returnProperties(), vox_i.returnProperties()

def kD_to_fg(mass_in_kD):
	'''Transforms a mass in kilodaltons to femtograms
	
	Arguments:
		mass_in_kD {[float]} -- [Mass in kD]
	
	Returns:
		[float] -- [mass in femtograms]
	'''
	return mass_in_kD*1.66054e-21*10**15

class Macromolecule:
	'''Creates a macromolecule object that has a certain mass, radius, volume, and diffusivity;
		Also accepts an optional input parameter, "number", or the number of macromolecules of the type that exist.
		If this number is given, the object also has a total mass and total volume.
	'''
	def __init__ (self,mass,radius,*num):
		self.mass = mass
		self.rad = radius
		self.vol = (4/3)*np.pi*(radius)**3
		K = 1.380*10**-23 # K =1.380*10**-23 (kg*m^2)/(s^2*K)
		T = 310 # T= 310K
		ETTA = 6.9*10**-4 #etta= 6.9*10**-4 #(kg/m*s)
		self.diffusivity = (K*T)/(6*np.pi*ETTA*(radius*10**-6))*10**12 #kT/(6*pi*etta*a) µm^2/s. a is in microns but is converted to meters to fit units. 
																		#The whole quantity is then multiplied by 1e12 to convert from m^2/s to µm^2/s
		if(num):
			self.num = num[0]
			self.mass_tot = self.num * mass
			self.vol_tot = self.num * self.vol

	def printProperties(self):
		try:
			print("\nNumber: ", self.num, "\n", "Mass: ", self.mass, "\n", "Radius: ", self.rad,
				  "\n Vol: ", self.vol, "\n Total mass: ", self.mass_tot, "\n Total volume: ", 
				  self.vol_tot,"\n Short time diffusivity: ", self.diffusivity)
		except AttributeError:
			print("\n", "Mass: ", self.mass, "\n", "Radius: ", self.rad,
				  "\n Vol: ", self.vol, "\n Short time diffusivity: ", self.diffusivity)

class Cell:
	''' Creates a Cell object that is paramterized with certain mass, volume, ribosome Macromolecule object, ternary complex Macromolecule object, crowder Macromolecule object, and nucleoid volume fraction.
		The object then computes the number/mass/volume of crowders it has as well as the volume fraction of each of its parameters.
	'''
	def __init__(self, cell_mass, cell_vol, rib, tern,crowder,nucleoid_volfrac):
		self.mass = cell_mass
		self.vol = cell_vol
		self.rib = rib
		self.tern = tern
		self.nucleoid_volfrac = nucleoid_volfrac
		
		self.crowder = crowder
		self.crowder.mass_tot = (self.mass - self.rib.mass_tot - self.tern.mass_tot)
		self.crowder.num = self.crowder.mass_tot/self.crowder.mass
		self.crowder.vol_tot = self.crowder.vol * self.crowder.num
		
		self.rib_volfrac = (self.rib.vol_tot/self.vol) #Calculates volume fraction of ribosome in the whole cell (not just outside nucleoid)
		self.tern_volfrac = self.tern.vol_tot/self.vol
		self.crowder_volfrac = self.crowder.vol_tot/self.vol
		self.volfrac_tot = self.rib_volfrac+self.tern_volfrac+self.crowder_volfrac

	def printProperties(self):
		print("\nMass: ", self.mass, "\n Volume: ", self.vol, "\n Rib vol frac: ", self.rib_volfrac,
			 "\n Tern vol frac:", self.tern_volfrac, "\n Crowder vol frac: ", self.crowder_volfrac, 
			  "\n Total vol frac:", self.volfrac_tot)

	def returnProperties(self):
		return self.vol,[self.rib_volfrac,self.tern_volfrac,self.crowder_volfrac,self.volfrac_tot],[self.rib.num,self.tern.num,self.crowder.num]

class Voxel:
	''' Creates a voxel object, based on a cell object, that represents a nucleoid-excluded cube region of the cell cytoplasm where translation occurs.
	Takes as input the number of ternary complexes that need to always be captured in the voxel.

	Creates paramters describing the number of ternary complexes, ribosomes, and crowders, as well as their volume fraction, in a voxel, and also the size of the voxel
	(size of voxel is tuned to maintain numTern ternary complexes in the voxel).    
	'''
	def __init__(self, numTern, Cell):
		self.numTern = numTern
		self.numRib = ( Cell.rib.num * (self.numTern/Cell.tern.num)/(1-Cell.nucleoid_volfrac) ) #Number of ribosomes in the nucleoid excluded region of space
		self.numCrowder =round( Cell.crowder.num*(self.numTern/Cell.tern.num) ) 
		
		self.vol = ( Cell.vol * (self.numTern/Cell.tern.num) )
		#self.vol = ( Cell.vol * (self.numRib/Cell.rib.num) )

		self.size = self.vol**(1/3) ##calculates edge length of voxel
		
		self.rib_volfrac = (self.numRib*Cell.rib.vol)/self.vol
		self.tern_volfrac = (self.numTern*Cell.tern.vol)/self.vol
		self.crowder_volfrac = (self.numCrowder*Cell.crowder.vol)/self.vol
		self.volfrac_tot = self.rib_volfrac + self.tern_volfrac+self.crowder_volfrac
	
	def printProperties(self):
		print("\n Volume: ", self.vol,"\n Voxel length: ", self.size, "\n Rib vol frac: ", self.rib_volfrac,
			 "\n Tern vol frac:", self.tern_volfrac, "\n Crowder vol frac: ", self.crowder_volfrac, 
			  "\n Total vol frac:", self.volfrac_tot,"\n Voxel num tern: ", self.numTern, 
			  "\n Voxel num rib: ", self.numRib, "\n Voxel num crowder: ", self.numCrowder)
		
	def returnProperties(self):
		return self.size,[self.rib_volfrac,self.tern_volfrac,self.crowder_volfrac,self.volfrac_tot],[self.numRib,self.numTern,self.numCrowder]
# modified 4-9-15 


# function that controls:
#
# inputs:
# 	population: numpy 1D array
#	supplyEps: float
#	demandEps: float

import demandFun, supplyFun
import sympy as sym
from numpy import *
import populationGrowth as pG
import matplotlib.pylab as plt
import pdb

class Agent(object):
	# class for each power plant agent. 
	# Agents have: 
	#	 generation assets
	#	 associated cost function
	#	 permits
	#	 utility = [revenue, carbon, risk]
	# 	 costs = [gas, nuclear, wind]
	#	 damping factor 
	""" name, quantity supplied, nuclear, gas, wind, turn)"""
	

	def __init__(self, name,  Nvariables, numTurns, numMoves):
		self.name = name
		self.numGenTypes = Nvariables
		self.numTurns = numTurns

		# default values for floats
		self.permits = 0 
		self.bank = 0
		self.ID = 1

		# variables defined by the agent parameters
		self.assets = zeros((Nvariables,1))
		self.utilityCoeff = zeros((Nvariables,1))
		self.carbon = zeros((Nvariables,1))
		self.costs = zeros((Nvariables,1))

		# location variables
		self.location = zeros((2, numMoves+1))
		self.searchRadius = 2 # default value


		# variables that are stored each turn 
		self.delta = zeros((numTurns, 1))
		self.production = zeros((numTurns, 3))
		self.utility = zeros((numTurns, 1))
		self.production_expected = zeros((numTurns, 1))
		self.supply = zeros((numTurns, 1))
		self.utilization = array([])
		self.utilizationRate =  zeros((numTurns, 1))
		self.oppProduction = zeros((numTurns, 1))
		self.damping = zeros((numTurns, 1))
		self.CO2_oppExpected = zeros((numTurns, 1))
		self.CO2 = zeros((numTurns, 1))
		self.zeta = zeros((numTurns, 1))
		self.revenue = zeros((numTurns, 1))
		self.competition = zeros((numTurns, 1))
		# turn counter
		self.turn = 0
		self.move = 0


	def assetValue(self, turn, nuclear, gas, wind):
		# define depreciation rate of each asset
		nuclearDep = .03
		windDep = .25
		gasDep = .1

		# define the capEX
		nuclearEX = 100.0
		windEX = 60.0
		gasEX = 30.0

		# for finding the asset value as depreciated
		def depreciation(period, rate, capEX):
			value = capEX*pow((1-rate),period)
			
			return value
		
		assets = depreciation(turn, nuclearDep, nuclearEX) +depreciation(turn, windDep, windEX) + depreciation(turn, gasDep, gasEX)

		return assets 

	def utilityCalc(self, revenue, utilization, CO2, energyPrice):
		try:
			# for when used to evaluate list of array choices
			# optimalDone.py
			return (self.utilityCoeff[1]*utilization - self.utilityCoeff[2]*CO2.reshape(len(CO2), 1)) +(self.utilityCoeff[0]*revenue)
		except (TypeError, AttributeError) :
			# for when utility calc is used to evaluate actual results
			# main.py
			return self.utilityCoeff[1]*utilization - self.utilityCoeff[2]*CO2+ self.utilityCoeff[0]*revenue
	
	def totalAssets(self):
		return self.nuclear + self.wind + self.gas

	def maxAssets(self):
		return max(self.assets)

	def productionUpdate(self, production):
		self.production = append(self.production, production)

	def turnUpdate(self):
		self.turn = self.turn + 1 

	def moveUpdate(self):
		self.move = self.move + 1 

	def reset(self):
		self.delta = zeros((self.numTurns, 1))
		self.production = zeros((self.numTurns, 3))
		self.utility = zeros((self.numTurns, 1))
		self.production_expected = zeros((self.numTurns, 1))
		self.oppProduction = zeros((self.numTurns, 1))
		self.damping = zeros((self.numTurns, 1))
		self.CO2_oppExpected = zeros((self.numTurns, 1))
		self.CO2 = zeros((self.numTurns, 1))
		self.zeta = zeros((self.numTurns, 1))
		self.revenue = zeros((self.numTurns, 1))
		self.competition = zeros((self.numTurns, 1))

	def dampingUpdate(self):
		''' will update the production damping coefficient based on the 
			delta and actual production from the previous production paths '''
		
		# if abs(self.delta[self.turn]) < 1.5 and self.turn > 2:
		# 	alpha = (self.damping[self.turn-1, 0] + self.damping[self.turn - 2, 0]) / 2.0
		# else:
		# 	alpha = 1.0 / (1 + pow(1.1, (self.delta[self.turn, 0]))) + .5
		alpha = 1.0 / (1 + pow(1.1, (self.delta[self.turn, 0]))) + .5
		self.damping[self.turn, 0] = alpha


	def CO2damping(self, CO2actual):
		delta = (self.CO2_oppExpected[self.turn, 0] +self.CO2[self.turn, 0]) - CO2actual
		zeta = 1.0 / (1 + pow(1.1, delta )) + .5

		self.zeta[self.turn, 0] = zeta 

	def visableGrid(self, grid, taxGrid, testLocation): 
		''' 
		handles the geospatial aspects of code
		returns: 
			population = int
			competition = int
		'''


		[m,n,o] = shape(grid)

		# --------------------------------- #
		# - FIND THE WORKING GRID SECTION - #
		# --------------------------------- #

		centerX = self.location[0, self.move]  + (-self.searchRadius + testLocation[0]) 
		centerY = self.location[1, self.move]  + (-self.searchRadius + testLocation[1])

		if centerX >= n:
			centerX = n-1
		elif centerX <= 0:
			centerX = 0

		if centerY >= m: 
			centerY = m-1 
		elif centerY <= 0:
			centerY = 0

		# check to wrap matrix
		west = int(centerX - self.searchRadius -1)
		east = int(centerX + self.searchRadius+1)
		north = int(centerY + self.searchRadius+1)
		south = int(centerY - self.searchRadius -1)

		## ADD FEATURE
		# check to see if the location is outside the grid 
		if north >= m:
			north = m-1 
		if south <= 0:
			south = 0 
		if east >= n:
			east = n-1
		if west <= 0:
			west = 0

		# pdb.set_trace()
 		visableGrid = grid[west:east, south:north, :]

 		# find properties of the working grid
 		population = sum(visableGrid[:,:, 1])

 		# find the agents nearby 
 		agentLoc = nonzero(visableGrid[:,:,3])
 		nearbyAgentsID = []

 		if len(agentLoc[0]) != 0:
 			for pt in range(len(agentLoc[0])):

	 			nearbyAgentsID.append(visableGrid[agentLoc[0][pt], agentLoc[1][pt], 3])
	 	else:
	 		pdb.set_trace()

 		taxes = taxGrid[centerX, centerY, :]

 		if population == 0:
 			pdb.set_trace()

 		return population, taxes, nearbyAgentsID

 	def newLocation(self, square, grid):
 		''' 
 		determines how agents will move
 		currently, they will always move up/down
 		before moving left/right
 		'''
 		[m,n,o] = shape(grid)
 		bestSquare = asarray((0,0))

 		bestSquare[0] = square[0][0]
 		bestSquare[1] = square[1][0]

 		# convert the submatrix to the larger matrix
 		bestSquare[0] = bestSquare[0] + self.location[0, self.move] - self.searchRadius
		bestSquare[1] = bestSquare[1] + self.location[1, self.move] - self.searchRadius
 		direction = -self.location[:, self.move] + bestSquare

 		# pdb.set_trace()
 		if direction[1] > 0:
 			# move up
 			self.location[0, self.move+1] = self.location[0, self.move] 

 			if self.location[1, self.move] + 1 < m:
	 			self.location[1, self.move+1] = self.location[1,self.move] + 1
	 		else:
	 			self.location[1, self.move+1] = self.location[1,self.move]


 		elif direction[1] < 0: 
 			self.location[0, self.move+1] = self.location[0, self.move] 

 			if self.location[1, self.move] - 1 > 0:
 				self.location[1, self.move+1] = self.location[1,self.move] - 1 
	 		else:
	 			self.location[1, self.move+1] = self.location[1,self.move] 


 		else: 	# needs to move east/west
 			if direction[0] > 0:
 				# move west
 				self.location[1, self.move+1] = self.location[1, self.move] 

 				if self.location[0, self.move] +1 < n:
	 				self.location[0,self.move+1] = self.location[0,self.move] +1 
	 			else:
	 				self.location[0,self.move+1] = self.location[0,self.move] 

 			elif direction[0] < 0:
 				self.location[1, self.move+1] = self.location[1, self.move] 

 				if self.location[0,self.move] -1 > 0:
	 				self.location[0,self.move+1] = self.location[0,self.move] -1  
	 			else:
	 				self.location[0,self.move+1] = self.location[0,self.move]


def agent(turn, population, supplyEps, demandEps):

	numDemand = 10
	carryCap = 100
	# make prediction based on supply
	
	##  make prediction based on demand { 
	# create a bunch of stochiastic population growth models
	growthModels = zeros((carryCap, numDemand))
	TOI = []
	for i in xrange(0, numDemand-2):
		growthModels[:, i:(i+1)] = pG.simDSLogistic(carryCap, .5, 1)
		# interpolate for time of interest 
		TOI.append = interp(turn, growthModels[:, i], growthModels[:,i+1])

	# using P at TOI, generate demand curves for each growth model 
	demand = [demandFun.demandfun(pop, demandEps) for pop in TOI] 

	# make prediction based on CO2

	supply = supplyFun.supplyfun(supplyEps)

	Q = sym.symbols('Q')

	eqQ = [sym.solve(supply - D, Q) for D in demand]
	eqP = [supply(EQ) for EQ in eqQ]

	return eqQ, eqP


def optimizationMatrix(*Agent):
	i = 0

	numAgent = len(Agent)

	cost = array([])
	
	# find the maximum number of assets
	maxAssets = 0
	for agent in Agent:
		numGenTypes = agent.numGenTypes
		if agent.maxAssets() > maxAssets:
			maxAssets = agent.maxAssets()

	utilization = zeros((1, numGenTypes*numAgent))
	supplyMatrix = zeros((maxAssets + 1, numAgent * numGenTypes ))
	
	# add padding so everyone has the matrix is even
	itr = 0
	for agent in Agent:
		for col in range(numGenTypes):
			utilization[0,col] = agent.assets[col]
			supplyMatrix[(maxAssets +1 - agent.assets[col]):, itr] = arange(1, agent.assets[col]+1)
			itr = itr +1 

	utilization = tile(utilization, (maxAssets+1,1))
	return supplyMatrix, utilization


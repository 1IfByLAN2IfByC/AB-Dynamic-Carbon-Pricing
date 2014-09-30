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

class Agent(object):
	# class for each power plant agent. 
	# Agents have: 
	#	 generation assets
	#	 associated cost function
	#	 permits
	""" name, quantity supplied, nuclear, gas, wind, turn)"""
	

	def __init__(self, name, Qsupplied, nuclear, gas, wind, permits=0.0):
		self.name = name
		self.Q = Qsupplied
		self.nuclear = nuclear
		self.gas = gas
		self.wind = wind
		self.permits = permits 
		# self.turn = turn 

	def prodCost(self, nuclear, gas, wind):
		# assign per MW costs 
		nuclearC = 2.0
		gasC = 4.0
		windC = 0.0

		prodcost = nuclear*nuclearC + gas*gasC + wind*windC

		return prodcost


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

	def maxAssets(self):
		return max(self.nuclear, self.wind, self.gas)

	#def CO2gen(self, nuclear, wind, 

def agent(turn, population, oppSupply, supplyEps, demandEps):

	numDemand = 10
	carryCap = 100
	# make prediction based on supply
	
	##  make prediction based on demand { 
	# create a bunch of stochiastic population growth models
	growthModels = zeros((carryCap, numDemand))
	TOI = []
	for i in xrange(0, numDemand-1):
		growthModels[:, i:(i+1)] = pG(carryCap, .5, 1)
		# interpolate for time of interest 
		TOI.append = interp(turn, growthModels[:, i], growthModels[:,i+1])

	# using P at TOI, generate demand curves for each growth model 
	demand = [demandFun.demandfun(pop, demandEps) for pop in TOI] 

	# make prediction based on CO2
	supply = supplyFun.supplyfun(supplyEps)

		
	Q = sym.symbols('Q')

	eqQ = [sym.solve(supply - D, Q) for D in demand]

	# find optimal agent output from subtracting opponent's expected supply from the eqQ 
	agentQ = [q[0] - oppSupply for q in eqQ] 	# slight hackery here. eqQ is a list-in-list? 
	
	
	return agentQ


def optmizationMatrix(*Agent):
	types = ['nuclear', 'gas', 'wind']
	numRow = 0
	numAgent = 0
	i = 0

	# find the maximum number of assets
	for agent in Agent:
		numAgent = numAgent + 1
		
		if numRow < agent.maxAssets():
			numRow = agent.maxAssets()
		else:
			pass

	supplyMatrix = zeros((numRow + 1, numAgent * len(types) ))
	
	# add padding so everyone has the same number of assets
	for agent in Agent:
		for t in types:
			num = getattr(agent, t)
			if num == numRow:
				supplyMatrix[:, i] = range(0, num + 1) #+1 range stops at x-1

			elif num < numRow:
				supplyMatrix[0:(numRow - num), i] = 0
				supplyMatrix[(numRow - num):, i] = range(0, num +1)
			else:
				print('ERROR: the number of rows counter broke')

			i  = i + 1 
	
	return supplyMatrix






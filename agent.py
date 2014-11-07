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
	#	 utility = [revenue, carbon, risk]
	# 	 costs = [gas, nuclear, wind]
	#	 damping factor 
	""" name, quantity supplied, nuclear, gas, wind, turn)"""
	

	def __init__(self, name, nuclear, gas, wind, utilityCoeff, costs, damping, bank, numTurns, permits=0.0):
		self.name = name
		self.nuclear = nuclear
		self.gas = gas
		self.wind = wind
		self.permits = permits 
		self.assets = array([[nuclear, gas, wind]])
		self.utilityCoeff = utilityCoeff
		self.damping = array([damping])
		self.delta = array([])
		self.production = zeros((numTurns, 3))
		self.costs = array(costs)
		self.coefficents = 0.0
		self.bank = bank
		self.utility = array([])
		self.production_expected = array([])
		self.supply = array([])
		self.utilization = array([])


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

	def totalAssets(self):
		return self.nuclear + self.wind + self.gas

	def maxAssets(self):
		return max(self.nuclear, self.wind, self.gas)

	def productionUpdate(self, production):
		self.production = append(self.production, production)

	def dampingUpdate(self):
		''' will update the production damping coefficient based on the 
			delta and actual production from the previous production paths '''
		# if len(self.delta) > 2:

		#YOU WERE STONED AND CHANGED THIS PART TO BE BACKWARDS
		if abs(self.damping[-1] - 1) < .1 and self.delta[-1] > 0:
			diff = 1 - self.damping[-1] 
			alpha = self.damping[-1] - (diff / 2)
		elif abs(self.damping[-1] - 1) < .1 and self.delta[-1] < 0:
			diff = 1 - self.damping[-1] 
			alpha = self.damping[-1] + (diff / 2)
		else:	
			alpha = 1. / (1.0 + pow(.9, -(self.delta[-1]))) + .5
	

		# if self.delta[-1] < 0:
		# 	alpha = 1.0 / (1+exp(-self.delta[-1])) -.5
		# elif self.delta[-1] > 0:
		# 	alpha = 1.0 / (1+exp(-self.delta[-1])) +.5
		# else:
		# 	print 'it has converged'
		# 	alpha = 1 
		self.damping = append(self.damping, alpha)


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
	types = ['nuclear', 'gas', 'wind']
	numRow = 0
	numAgent = 0
	i = 0

	utilization = array([])
	cost = array([])

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
		utilization = hstack((utilization, [getattr(agent, 'nuclear'), getattr(agent, 'gas'), getattr(agent, 'wind')]))
		# cost = hstack((cost, [costNuc, costGas, costWind]))
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

	# turn utility vector into a matrix
	utilization = ones((numRow + 1, numAgent*len(types))) * utilization

	return supplyMatrix, utilization


# modified 4-9-15 

from numpy import *
import agent
import time
import optimizeDone, equilibrium
from pprint import pprint 
import sympy as sym
import matplotlib.pylab as plt
import pdb 
reload(agent)
reload(optimizeDone)

time0 = time.time()


#  define the parameters 
# numPlayers = 3 # disable if using geo
numBidsPerTurn = 20
numGenTypes = 3
numMovingTurns = 10
deps = .2
# population = 15 # disable if using geo 
numShuffles = 100
maxCO2 = 10
CO2tax = 0
demandResolution = .1 

# preallocate the matrix 
Q = zeros((1, numBidsPerTurn)) 
total_utility = zeros((1, numBidsPerTurn))
total_revenue = zeros((1, numBidsPerTurn))
total_CO2 = zeros((1, numBidsPerTurn))
eq_price = zeros((1, numBidsPerTurn))

# ----------------------------------------#
# ---------- DEFINE THE AGENTS ---------- # 
# ----------------------------------------#
opp1 =agent.Agent('opp1', numGenTypes, numBidsPerTurn)
michael = agent.Agent('michael', numGenTypes, numBidsPerTurn)
opp = agent.Agent('opp', numGenTypes, numBidsPerTurn)

agents = [opp, opp1, michael]

# define agent 1
          # nuc, gas, wind
allocation = (6, 5, 10) 
costs =      (5.3, 2.8, 6.0) 
carbon =     (.1, 2.0, 0.0)
coeff = (.7, .2, .1)
location = (0,0)


opp1.assets = asarray(allocation)
opp1.costs = asarray(costs)
opp1.carbon = asarray(carbon)
opp1.utilityCoeff = asarray(coeff)
opp1.location = location

# define agent 2 
          # nuc, gas, wind
allocation = (10, 6, 6) 
costs =      (4.6, 2.6, 7.0) 
carbon =     (.1, 2.0, 0.0)
coeff = (.7, .2, .1)
location = (5,2)


opp.assets = asarray(allocation)
opp.costs = asarray(costs)
opp.carbon = asarray(carbon)
opp.utilityCoeff = asarray(coeff)
opp.location = location

# define agent 3 
          # nuc, gas, wind
allocation = (4, 10, 6) 
costs =      (4.8, 2.4, 7.0) 
carbon =     (.1, 2.0, 0.0)
coeff = (.7, .2, .1)
location = (6,9)


michael.assets = asarray(allocation)
michael.costs = asarray(costs)
michael.carbon = asarray(carbon)
michael.utilityCoeff = asarray(coeff)
michael.location = location

# create the optimization matrix for each player 
# 	- this will consist of a matrix buffered by zeros 
# 	corresponding with the max resource
for a in agents: 
	a.supply, a.utilization = agent.optimizationMatrix(a)

#---------------------------------#	
# --- CREATE THE DEMAND CURVE --- #
#---------------------------------#

# define demand variables 
D = sym.symbols('D')
q = sym.symbols('Q')

demand = population - deps * q

price_supply = arange(0, agents[0].maxAssets() / demandResolution, demandResolution)
price_supply = [demand.evalf(subs={q:ps}) for ps in price_supply]

#--------------------------------#
# ------- CREATE GRID ---------- #
#--------------------------------#

grid = zeros((15, 15, 4))
randPop = [[random.rand() for x in xrange(15)] for y in xrange(15)]
grid[:,:, 1] = randPop

taxGrid = ones((15,15, numGenTypes))*random.rand()


# ------------------------------ #
# -- BEGIN GRID POINTS SEARCH -- # 
# ------------------------------ #

for move in range(numMovingTurns):

	for player in agents:
		# create utility storing matrix
		utilityMap = zeros((player.searchRadius*2+1 , player.searchRadius*2+1))

		for i in range(player.searchRadius*2+1): 
			for j in range(player.searchRadius*2+1):

				population, numPlayers = player.visableGrid(grid, [i,j])

				# taxes is returned as a tuple (nuclear, gas, wind)
				taxes = taxGrid[i,j,:].reshape(numGenTypes, 1)

				# reset the turn counter
				player.turn = 0
				for k in xrange(0, numBidsPerTurn-1):
					# print 'Begin turn %s' % k
					Q_actual = 0.0
					CO2_actual = 0.0

					# loop through to find what agent's will produce based on their expectations
					for A in agents:
						if k != 0:
							# update predictive variables
							A.oppProduction[k, 0] = A.oppProduction[k-1, 0] * A.damping[k-1, 0]
							A.CO2_oppExpected[k, 0] = A.CO2_oppExpected[k-1, 0] * A.zeta[k-1, 0]

							# find values for this turn
							A.production[k, :], A.utilizationRate[k, 0] = optimizeDone.optimize(A, price_supply,\
							 taxes, CO2tax, maxCO2, numPlayers, numShuffles, k)
							A.production_expected[k, 0] = sum(A.production[k, :]) + A.oppProduction[k, 0]
							A.CO2[k, 0] = dot(A.production[k, :], A.carbon)
						
						else:
							print 'first turn, assuming no damping'
							A.production[k, :], A.utility[k, 0] = optimizeDone.optimize(A,\
							 price_supply, taxes, CO2tax, maxCO2, numPlayers, numShuffles, k)
							A.production_expected[k, 0] = sum(A.production[k, :]) * numPlayers 
							A.CO2[k, 0] = dot(A.production[k, :], A.carbon)
							A.CO2_oppExpected[k, 0] = A.CO2[k, 0]
							
						# for each agent append their production to find the 
						# total production values 
						Q_actual = Q_actual + sum(A.production[k, :])
						CO2_actual = CO2_actual + A.CO2[k, 0]
										
					## FIND THE ACTUAL PRICE
					eq_price[0, k] = demand.evalf(subs={q:Q_actual})
					Q[0, k] = Q_actual
					total_CO2[0, k] = CO2_actual	

					#pdb.set_trace()
					for A in agents:
						if k == 0:
							A.oppProduction[k, 0] =  Q_actual - sum(A.production[k])

						# check to see if surpasses the predefined max CO2
						if total_CO2[0, k] >= maxCO2:
							A.revenue[k,0] = sum(A.production[k]*eq_price[0,k] - A.production[k]*A.costs - A.production[k]*taxes)  - A.CO2[k,0] * CO2tax
							A.utility[k,0] = A.utilityCalc(A.revenue[k, 0], A.utilizationRate[k, 0], A.CO2[k, 0], eq_price[0, k])

						else:
							A.revenue[k,0] = sum(A.production[k]*eq_price[0,k] - A.production[k]*A.costs - A.production[k]*taxes)
							A.utility[k,0] = A.utilityCalc(A.revenue[k, 0], A.utilizationRate[k, 0], 0, eq_price[0, k])

						total_utility[0, k] = A.utility[k] + total_utility[0, k]
						total_revenue[0, k] = total_revenue[0, k] + A.revenue[k, 0]
						A.bank = A.bank + A.revenue[k, 0]
						A.delta[k, 0] =  A.production_expected[k] - Q[0, k] 
						A.CO2damping(CO2_actual)
						A.dampingUpdate()

						A.turnUpdate()

				# store the steady state utility
				utilityMap[i,j] = total_revenue[-1, 0]

		# pick the best square
		bestSq = utilityMap.argmax()

		# move towards that square 
		player.move(bestSq)

		## the player has moved, end their turn




t = arange(0, numBidsPerTurn)
T = arange(0, numBidsPerTurn+1)

print 'the code took %s seconds to run' %(time.time()-time0)



# fig = plt.figure()
# plt1 = fig.add_subplot(3,2,1)
# plt1.plot(t, michael.delta, label='Agent 1 delta')
# plt1.plot(t, opp.delta, label='Agent 2 delta')
# plt1.plot(t, opp1.delta, label='Agent 3 delta')
# plt1.plot(t, brit.delta, label='Agent 4 delta')
# plt1.legend()


# plt2 =fig.add_subplot(3,2,2)
# plt2.plot(t, michael.damping, label = 'Agent 1 damping')
# plt2.plot(t, opp.damping, label='Agent 2 damping')
# plt2.plot(t, opp1.damping, label='Agent 3 damping')
# plt2.plot(t, brit.damping, label='Agent 4 damping')
# plt2.plot(t, ones((len(t), 1)))
# plt2.legend()


# plt3 = fig.add_subplot(3,2,3)
# plt3.plot(t, sum(michael.production, 1), label='Agent 1 Production')
# plt3.plot(t, sum(opp.production, 1), label='Agent 2 Production')
# plt3.plot(t, sum(opp1.production, 1), label='Agent 3 Production')
# plt3.plot(t, sum(brit.production, 1), label='Agent 4 Production')
# plt3.plot(t, Q.transpose(), label='Total Production')
# plt3.legend()

# plt4 = fig.add_subplot(3,2,4)
# plt4.plot(t, michael.production_expected, label='Agent 1 mod. expecations')
# plt4.plot(t, opp.production_expected, label='Agent 2 mod. expecations')
# plt4.plot(t, opp1.production_expected, label='Agent 3 mod. expecations')
# plt4.plot(t, brit.production_expected, label='Agent 4 mod. expecations')
# plt4.plot(t, Q.transpose(), label='Total Production')
# plt4.legend()

# plt5 = fig.add_subplot(3,2,5)
# plt5.plot(t, total_utility.transpose(), label='Percent Combined Utility Growth Over Time')
# plt5.plot(t, total_revenue.transpose() , label='Percent Revenue Growth Over Time')
# plt5.legend()

# plt6 = fig.add_subplot(3,2,6)
# # plt6.plot(t, total_CO2.transpose(), label='Total CO2 Emissions')
# # plt6.plot(t, ones((numBidsPerTurn, 1))*maxCO2, label='CO2 Threshold')
# plt6.scatter(Q, eq_price, label='Q v. P')
# plt6.legend()

# fig.show()




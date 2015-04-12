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
numPlayers = 3
numTurns = 20
numGenTypes = 3
deps = .2
population = 15
numIters = 100
maxCO2 = 10
CO2tax = 0
demandResolution = .1 

# preallocate the matrix 
Q = zeros((1, numTurns)) 
total_utility = zeros((1, numTurns))
total_revenue = zeros((1, numTurns))
total_CO2 = zeros((1, numTurns))
eq_price = zeros((1, numTurns))

# ----------------------------------------#
# ---------- DEFINE THE AGENTS ---------- # 
# ----------------------------------------#
opp1 =agent.Agent('opp1', numGenTypes, numTurns)
michael = agent.Agent('michael', numGenTypes, numTurns)
opp = agent.Agent('opp', numGenTypes, numTurns)

agents = [opp, opp1, michael]

# define agent 1
          # nuc, gas, wind
allocation = (6, 5, 10) 
costs =      (5.3, 2.8, 6.0) 
carbon =     (.1, 2.0, 0.0)
coeff = (.7, .2, .1)


opp1.assets = asarray(allocation)
opp1.costs = asarray(costs)
opp1.carbon = asarray(carbon)
opp1.utilityCoeff = asarray(coeff)

# define agent 2 
          # nuc, gas, wind
allocation = (10, 6, 6) 
costs =      (4.6, 2.6, 7.0) 
carbon =     (.1, 2.0, 0.0)
coeff = (.7, .2, .1)


opp.assets = asarray(allocation)
opp.costs = asarray(costs)
opp.carbon = asarray(carbon)
opp.utilityCoeff = asarray(coeff)

# define agent 3 
          # nuc, gas, wind
allocation = (4, 10, 6) 
costs =      (4.8, 2.4, 7.0) 
carbon =     (.1, 2.0, 0.0)
coeff = (.7, .2, .1)

michael.assets = asarray(allocation)
michael.costs = asarray(costs)
michael.carbon = asarray(carbon)
michael.utilityCoeff = asarray(coeff)

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

## initialize production
i = 0

for k in xrange(0, numTurns):
	print 'Begin turn %s' % k
	Q_actual = 0.0
	CO2_actual = 0.0


	# loop through to find what agent's will produce based on their expectations
	for A in agents:
		if k != 0:
			A.oppProduction[k, 0] = A.oppProduction[k-1, 0] * A.damping[k-1, 0]
			A.CO2_oppExpected[k, 0] = A.CO2_oppExpected[k-1, 0] * A.zeta[k-1, 0]
			A.production[k, :], A.utilizationRate[k, 0] = optimizeDone.optimize(A, price_supply,\
			 CO2tax, maxCO2, numPlayers, numIters, k)
			A.production_expected[k, 0] = sum(A.production[k, :]) + A.oppProduction[k, 0]
			A.CO2[k, 0] = dot(A.production[k, :], A.carbon)
		
		else:
			print 'first turn, assuming no damping'
			A.production[k, :], A.utility[k, 0] = optimizeDone.optimize(A,\
			 price_supply, CO2tax, maxCO2, numPlayers, numIters, k)
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
			A.revenue[k,0] = sum(A.production[k]*eq_price[0,k] - A.production[k]*A.costs) - A.CO2[k,0] * CO2tax
			A.utility[k,0] = A.utilityCalc(A.revenue[k, 0], A.utilizationRate[k, 0], A.CO2[k, 0], eq_price[0, k])

		else:
			A.revenue[k,0] = sum(A.production[k]*eq_price[0,k] - A.production[k]*A.costs)
			A.utility[k,0] = A.utilityCalc(A.revenue[k, 0], A.utilizationRate[k, 0], 0, eq_price[0, k])

		total_utility[0, k] = A.utility[k] + total_utility[0, k]
		total_revenue[0, k] = total_revenue[0, k] + A.revenue[k, 0]
		A.bank = A.bank + A.revenue[k, 0]
		A.delta[k, 0] =  A.production_expected[k] - Q[0, k] 
		A.CO2damping(CO2_actual)
		A.dampingUpdate()

		A.turnUpdate()


t = arange(0, numTurns)
T = arange(0, numTurns+1)

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
# # plt6.plot(t, ones((numTurns, 1))*maxCO2, label='CO2 Threshold')
# plt6.scatter(Q, eq_price, label='Q v. P')
# plt6.legend()

# fig.show()




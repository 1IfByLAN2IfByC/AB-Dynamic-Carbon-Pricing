# modified 4-9-15 

#function that will use modified genetic algo to find optimas
# inputs:
	# matrix:
		# rows  = all possible production values
		# columns = player/production values
	# cost fun = the cost functions for each production type
	# number of iterations
	# scalar demand

from numpy import *
import time
import pdb 
import equilibrium
import sympy as sym
def optimize(Agent, priceArray, margTax, maxCO2, numPlayers, maxIter, turn):
	t = time.time()
	[m, n] = shape(Agent.supply)

	maxUtilityCombo = zeros((maxIter,n))
	maxUtilityScalar = zeros((maxIter, 1))
	maxUtilization = zeros((maxIter, 1))
	maxRevenue = zeros((maxIter, 1))

	# set monopolist or no
	mono = False
	matrix = Agent.supply

	for i in xrange(0, maxIter):
		[m, n] = shape(Agent.supply) # number of rows changes with each iteratio

		map(random.shuffle, Agent.supply.T)
		supply = dot(Agent.supply, ones((n,1))) 

		## ADJUST THE MATRIX BASED ON DAMPING FUNCTION
		if Agent.production_expected[turn] == 0:
			aggSupply = numPlayers* dot(Agent.supply, ones((n,1))) 
			CO2 = numPlayers* dot(Agent.supply, Agent.carbon) 

		else:
			aggSupply = dot(Agent.supply, ones((n,1))) +\
				Agent.oppProduction[turn]*ones((m,1))

			CO2 = dot(Agent.supply, Agent.carbon).reshape(m, 1) + \
				Agent.CO2_oppExpected[turn]*ones((m, 1))

		if mono == True:
			supply = aggSupply

		# round to 2 decimal places and multiply by 10 to get price index
		Qsupplied = array([round(s, 2) * 10 for s in aggSupply]).reshape(m,1)
		# pdb.set_trace()
		energyPrice = [priceArray[int(q)] for q in Qsupplied]
		energyPrice = array(energyPrice).reshape(m, 1)

		# FIND UTILIZATION, REVENUE
		# here is the pretax revenue, i.e. price*quantity - quantity*costs
		revenueDecoupled = ( supply* energyPrice ) - (dot(Agent.supply, Agent.costs.reshape(n,1))) 
		utilizationRate = dot(1 - ((Agent.utilization - Agent.supply) / Agent.utilization), ones((n,1)))

		# check to see if the total supply is greater than equal to demand
		# drop if the total utility is negative
		deleteRow = []
		taxedCombos = zeros((1, m))

		# pdb.set_trace()
		for k in xrange(0,m):
		# if revenue is neg., drop combo
		# if CO2 level is greater than max lvl impose tax
		    if revenueDecoupled[k,0] <= 0:
		        deleteRow.append(k)
		    if CO2[k] >= maxCO2:
		        taxedCombos[0, k] = 1

		# IF CO2 LEVELS ARE GREATER, ADD THE MARGINAL TAX TO COSTS

		taxLosses = taxedCombos * CO2.reshape(1,m)*margTax

		# drop all the combinations that coincide with negative revenue
		# revenue = delete(revenue, deleteRow, 0)
		utilizationRate = delete(utilizationRate, deleteRow, 0)
		matrixCal = delete(Agent.supply, deleteRow, 0)
		revenueDecoupled = delete(revenueDecoupled, deleteRow, 0)
		energyPrice = delete(energyPrice, deleteRow, 0)
		taxLosses = delete(taxLosses, deleteRow, 1)
		CO2 = delete(CO2, deleteRow)

		revenueDecoupled = revenueDecoupled - taxLosses.transpose()

		# for i in xrange(0, numPlayers):
		# 	if i !=0:
		# 		begin = i*numGenTypes
		# 		end = begin+numGenTypes
		# 		matrix[:,begin: end] = matrix[:, begin:end] * expectation
		# 	else:
				# pass

		# check to make sure utility vector has values
		# i.e. that not all the combinations yielded negative rev.
		# pdb.set_trace()
		try:
			utility = Agent.utilityCalc(revenueDecoupled, utilizationRate, CO2, energyPrice)
			maxCombo = utility.argmax()
			maxUtilityCombo[i, :] = matrixCal[maxCombo, :]
			maxUtilityScalar[i, 0] = utility[maxCombo, 0]
			maxUtilization[i, :] = utilizationRate[maxCombo, :]
			maxRevenue[i,0] = revenueDecoupled[maxCombo, 0]
			# pdb.set_trace()
                
		except ValueError:
			print ' error in utility calcs'
		else:
			pass


	# after the maximum amount of shifts has occured, find the highest utility combo
	maximumU = maxUtilityScalar.argmax()

	maxU = maxUtilityScalar[maximumU, 0]
	optimalCombo = maxUtilityCombo[maximumU, :]
	optimalUtilization = maxUtilization[maximumU, 0]

	# pdb.set_trace()
	# print(time.time() - t)
	# print 'optimal combo is: ' + str(optimalCombo)
	# print 'the max utility is: ' + str(maxU)
	# print 'the market price is: {}'.format(demand.evalf(subs={Q: sum(optimalCombo)}))
	# print 'the demand is: ' + str(eqD)
	# print 'the supply is: ' + str(sum(optimalCombo))
	# print 'the maximum revenue is: {}'.format(maxRevenue)
	# print matrix

	return optimalCombo, optimalUtilization
	# return maxUtilityCombo, maxUtilityScalar, eqD , maxUtilization, maxRevenue

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
def optimize(Agent, matrixIN, utilizationMatrix, expectation, priceArray, numPlayers, maxIter):
	t = time.time()
	[m, n] = shape(matrixIN)
	numGenTypes = int(n/numPlayers)

	maxUtilityCombo = zeros((maxIter,n))
	maxUtilityScalar = zeros((maxIter, 1))
	maxUtilization = zeros((maxIter, 1))
	maxRevenue = zeros((maxIter, 1))

	# elastiticy variables
	deps = .1
	seps = .2

	# make deep copy of the input array for mutation
	matrix = matrixIN.copy()

	# create cost vector
	# each player assumes all other players face the same costs
	costFun = tile(Agent.costs, numPlayers)

	# solve for demand given population
	# demand = equilibrium.demandfun(population, deps)
	# eqD = equilibrium.equilibrium(demand, seps)
	# Q = sym.symbols('Q')

	# find the percent of total capacity each firm has
	# capShare = [i / sum(totalAss) for i in totalAss]
	# capShare = array(capShare)

	## calculate the cost for a range of supplies
	# price_supply = arange(0,sum(supply[-1]), .1)
	# price_supply = [demand.evalf(subs={Q:ps}) for ps in price_supply]
	price_supply = priceArray

	def marketSharing(matrix, m, n, capShare, numPlayers):
		numGenTypes = int(n/numPlayers)
		percent = zeros((numPlayers, 1))
		for P in xrange(0, numPlayers):
			percent = sum(matrix[ (P*n/numPlayers), (P+1)*n/numPlayers])
			percent = percent / capShare
 	
 	# pdb.set_trace()

	for i in xrange(0, maxIter):
		# as a check system, print the horizontal sum of the row
		# should change every time or so
		# print dot(matrix, ones((n,1)))
		# print '/n'
		[m, n] = shape(matrix) # number of rows changes with each iteration

		# shift the key down
		def shuffle(matrix, m, n, turn):
			key = (turn+m)%m
			# print key
			for j in xrange(0, n):
				shift = (key+j)%m
				tmp = matrix[shift, j]

				if shift + 1 < m-1: # -1 because shape gives abs. not placement
					matrix[shift, j] = matrix[ (shift+1), j]
					matrix[(shift+1), j] = tmp

				else:
					matrix[shift, j] = matrix[0, j]
					matrix[0, j] = tmp

			return matrix

		matrix = shuffle(matrix, m, n, i)

		# find aggregate supply and solve for price
		supply = dot(matrix, ones((n,1)))
		# round to 2 decimal places and multiply by 10 to get price index
		Qsupplied = array([round(s, 2) * 10 for s in supply]).reshape(m,1)

		# pdb.set_trace()

		energyPrice = [price_supply[int(q)] for q in Qsupplied]
		energyPrice = array(energyPrice).reshape(m, 1)

		playerSupply = zeros((m, numPlayers))
		revenueDecoupled = zeros((m, numPlayers))


		
		# pdb.set_trace()
		for i in xrange(0,numPlayers):
			begin = i*numGenTypes
			end = begin+numGenTypes
			if i == 0:
				playerSupply[:,i] = sum(matrix[:, begin:end], 1)
			else:
				playerSupply[:,i] = sum(matrix[:, begin:end], 1)/ expectation
				matrix[:,begin: end] = matrix[:, begin:end] / expectation 

			revenueDecoupled[:, i] = list(playerSupply[:,i].reshape(m,1) * energyPrice - (dot(matrix[:, begin:end], costFun[begin:end])).reshape(13,1))
			
		# revenue = ( supply* energyPrice ) - (dot(matrix, costFun.reshape(n,1)))

		# merge the two reveuneDecoupled columns
		revenueDecoupled = sum(revenueDecoupled, 1).reshape(m,1)
		utilizationRate = dot(1 - ((utilizationMatrix - matrix) / utilizationMatrix), ones((n,1)))


		pdb.set_trace()
		# check to see if the total supply is greater than equal to demand
		# drop if the total utility is negative
		deleteRow = []
		for k in xrange(0,m):
			# if revenue is neg., drop combo
			if revenueDecoupled[k] <= 0:
				deleteRow.append(k)
			else:
				pass

		# drop all the combinations that coincide with negative revenue
		# revenue = delete(revenue, deleteRow, 0)
		utilizationRate = delete(utilizationRate, deleteRow, 0)
		matrixCal = delete(matrix, deleteRow, 0)
		revenueDecoupled = delete(revenueDecoupled, deleteRow, 0)

		for i in xrange(0, numPlayers):
			if i !=0:
				begin = i*numGenTypes
				end = begin+numGenTypes
				matrix[:,begin: end] = matrix[:, begin:end] * expectation
			else:
				pass

		# check to make sure utility vector has values
		# i.e. that not all the combinations yielded negative rev.
		try:
			# utility = (Agent.utilityCoeff[1]*utilizationRate*energyPrice[0]) +  (Agent.utilityCoeff[0]*revenueDecoupled[:,0] 
			# 	+ Agent.utilityCoeff[0]*expectation*revenueDecoupled[:,1]).reshape(len(utilizationRate),1)
			utility = (Agent.utilityCoeff[1]*utilizationRate * mean(energyPrice) +(Agent.utilityCoeff[0]*revenueDecoupled))
			maxCombo = utility.argmax()
			maxUtilityCombo[i, :] = matrixCal[maxCombo, :]
			maxUtilityScalar[i, 0] = utility[maxCombo, 0]
			maxUtilization[i, :] = utilizationRate[maxCombo, :]
			maxRevenue[i,0] = revenueDecoupled[maxCombo, 0]
		except ValueError:
			# print 'All production combinations were dropped \n'
			# print matrix
			pass
		else:
			pass

	# after the maximum amount of shifts has occured, find the lowest cost combo
	maximumU = maxUtilityScalar.argmax()
	# print maximumU

	maxU = maxUtilityScalar[maximumU, 0]
	optimalCombo = maxUtilityCombo[maximumU, :]

	# print(time.time() - t)
	# print 'optimal combo is: ' + str(optimalCombo)
	# print 'the max utility is: ' + str(maxU)
	# print 'the market price is: {}'.format(demand.evalf(subs={Q: sum(optimalCombo)}))
	# print 'the demand is: ' + str(eqD)
	# print 'the supply is: ' + str(sum(optimalCombo))
	# print 'the maximum revenue is: {}'.format(maxRevenue)
	# print matrix

	return optimalCombo, maxU
	# return maxUtilityCombo, maxUtilityScalar, eqD , maxUtilization, maxRevenue

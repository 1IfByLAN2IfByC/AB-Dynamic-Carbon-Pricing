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

def optimize(matrixIN, costFun, utilizationMatrix, population, maxIter):
	t = time.time()
	[m, n] = shape(matrixIN)
	maxUtilityCombo = zeros((maxIter,n))
	maxUtilityScalar = zeros((maxIter, 1))
	maxUtilization = zeros((maxIter, n))

	# elastiticy variables
	deps = .3
	seps = .2

	# make deep copy of the input array for mutation
	matrix = matrixIN.copy()

	# solve for demand given population
	demand = equilibrium.demandfun(population, deps)
	eqD = equilibrium.equilibrium(demand, seps)
	Q = sym.symbols('Q')

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
		energyPrice = [demand.evalf(subs={Q: q}) for q in supply]
		energyPrice = array(energyPrice).reshape(m, 1)

		revenue = ( supply* energyPrice ) - (dot(matrix, costFun.reshape(n,1)))
		utilizationRate = dot(1 - ((utilizationMatrix - matrix) / utilizationMatrix), ones((n,1)))
		variance = var(supply, 1)
		# check to see if the total supply is greater than equal to demand	
		# drop if the total utility is negative 
		deleteRow = []
		for k in xrange(0,m):
			# if revenue is neg., drop combo
			if revenue[k] <= 0: 
				deleteRow.append(k)
			else:
				pass

		# drop all the combinations that coincide with negative revenue
		revenue = delete(revenue, deleteRow, 0)
		utilizationRate = delete(utilizationRate, deleteRow, 0)
		matrixCal = delete(matrix, deleteRow, 0)
		# print revenue
	
		# check to make sure utility vector has values 
		# i.e. that not all the combinations yielded negative rev.
		try:
			# utility = ( .5* utilizationRate + .4* (revenue))
			
			maxCombo = utility.argmax()
			maxUtilityCombo[i, :] = matrixCal[maxCombo, :]
			maxUtilityScalar[i, 0] = utility[maxCombo, 0]
			maxUtilization[i, :] = utilizationRate[maxCombo, :]
		except ValueError:
			print 'All production combinations were dropped \n'
			print matrix
		else:
			pass

	# after the maximum amount of shifts has occured, find the lowest cost combo
	maximumU = maxUtilityScalar.argmax()
	# print maximumU

	maxU = maxUtilityScalar[maximumU, 0]
	optimalCombo = maxUtilityCombo[maximumU, :]

	print(time.time() - t)
	print 'optimal combo is: ' + str(optimalCombo)
	print 'the max utility is: ' + str(maxU)
	print 'the market price is: {}'.format(demand.evalf(subs={Q: sum(optimalCombo)}))
	print 'the demand is: ' + str(eqD)
	print 'the supply is: ' + str(sum(optimalCombo))
	print matrix


	return maxUtilityCombo, maxUtilityScalar, eqD , maxUtilization



		 	
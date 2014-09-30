
#function that will use modified genetic algo to find optimas
# inputs: 
	# matrix:
		# rows  = all possible production values
		# columns = player/production values
	# cost fun = the cost functions for each production type
	# number of iterations
	# scalar demand 

from numpy import *
from time import time


def optimize(matrix, costFun, demand, maxIter):
	t = time.time()
	[m, n] = shape(matrix)
	minCost = zeros((maxIter, n))
	optimalCombo = zeros((1,n))
	for i in xrange(0, maxIter):
		# identify the key 
		key = (i+m)%m 
		
		# shift the key down 
		for j in xrange(0, n):
			shift = (key+j)%m
                        tmp = matrix[shift, j] 
			#print(shift)
			if shift + 1 < m-1: # -1 because shape gives abs. not placement
				matrix[shift, j] = matrix[ (shift+1), j] 
				matrix[(shift+1), j] = tmp 

			else:
				matrix[shift, j] = matrix[0, j]
				matrix[0, j] = tmp
		# for testing purposes, print each shift
	#	print(key)
	#	print('\n')   
	#	print(matrix)	
	#	print('\n')
		# check to see if the total supply is greater than equal to demand	
		for k in xrange(0,m):
			supply = sum( matrix[k, :])
			if supply < demand: # if supply is less than demand, drop combo
				delete(matrix, k)
			else:
				pass
		
		# multiply the matrix by the cost function
		cost = dot(matrix, costFun.transpose())
		
		# find minimum cost 
		minCombo = cost.argmin()

		# append the minimum combo to the master set outside itereative loop
		minCost[i, :] = matrix[minCombo, :]

	# after the maximum amount of shifts has occured, find the lowest cost combo
	cost = zeros((maxIter, n))
	cost = dot(minCost, costFun.transpose())
	minCombo = minCost.argmin()
#	print(minCombo)
	print(time.time()-t)
	optimalCombo = minCost[minCombo, :]

	return optimalCombo

		 		




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

def optimize(matrix, costFun, utilizationMatrix, demand, maxIter):
	t = time.time()
	[m, n] = shape(matrix)
	maxUtilityCombo = zeros((maxIter,n))
	maxUtilityScalar = zeros((maxIter, 1))

	for i in xrange(0, maxIter):
		[m, n] = shape(matrix) # number of rows changes with each iteration
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
		deleteRow = []
		for k in xrange(0,m):
			supply = sum( matrix[k, :])
			if supply < demand: # if supply is less than demand, drop combo
				deleteRow.append(k)
			else:
				pass

		matrix = delete(matrix, deleteRow, 0)

		# multiply the matrix by the utility function
		utility = ( 2* dot( ((utilizationMatrix - matrix) / utilizationMatrix), ones((n,n)) )
		 + .8* dot(matrix, costFun))
		
		# find max array position of max utility 
		maxCombo = utility.argmax()

		# append the minimum combo to the master set outside itereative loop
		maxUtilityCombo[i, :] = matrix[maxCombo, :]
		maxUtilityScalar[0, i] = utility[maxCombo]

	# after the maximum amount of shifts has occured, find the lowest cost combo
	maximumU = maxUtilityScalar.argmax()

	MaxU = maxUtilityScalar[maximumU]
	optimalCombo = minCost[maximumU, :]

	print(time.time() - t)
	return optimalCombo, maxU, 

		 	
# function that contains the rules
# for population growth 

# inputs:
#	previous pop [vector]
#	awareness [int]
#	assumption [float]

from numpy import *

def populationGrowth(population, assumption, aware):
	pop = 0
	
	# check to see if it the first turn
	if len(population) < 2:
		# first turn
		pop = population[0] * (1+assumption)
		
	else:
	# take the average of the last 2 population growths
		pop = (population[:-1] + population[:-2]) / 2 
		
	
	# outputs
	return pop
	
	
	
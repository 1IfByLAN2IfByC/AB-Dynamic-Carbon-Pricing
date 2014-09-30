# function that contains the rules
# for CO2 growth 

# inputs:
#	previous CO2 [vector]
#	awareness [int]
#	assumption [float]

from numpy import *

def CO2Growth(CO2, assumption, aware):
	co2 = 0
	
	# check to see if it the first turn
	if len(CO2) < 2:
		# first turn
		co2 = co2[0] * (1+assumption)
		
	else:
	# take the average of the last 2 population growths
		co2 = (co2[:-1] + co2[:-2]) / 2 
		
	
	# outputs
	return co2
	
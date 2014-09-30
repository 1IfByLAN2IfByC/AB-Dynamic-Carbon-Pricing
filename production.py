# function that controls solving the demand function

import sympy as sym
from numpy import *

def demandfun(demand, assumption, randShock):
	
	# check to see if is initial period
	if len(demand) < 2:
		tmpDemand = demand[0] * (1 + assumption)
		
	else:
		tmpDemand = (demand[:-1] + demand[:-2]) /2 
	
	
	return demand.append(tmpDemand)
	
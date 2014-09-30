# function that controls solving the demand function

import sympy as sym
from numpy import *

def demandfun(demandAbs, elasticity):

	# of form:
	# demand = demand_(t-1) * (1+growth)

	demand, Q = sym.symbols('demand Q')
		
	demand = demandAbs  - (elasticity)*Q 
		
	return demand 
		
		

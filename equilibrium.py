# function that controls solving the demand function

import sympy as sym
from numpy import *

def demandfun(demandAbs, elasticity):

	# of form:
	# demand = demand_(t-1) * (1+growth)

	demand, Q = sym.symbols('demand Q')
		
	demand = demandAbs  - (elasticity)*Q 
		
	return demand 

def equilibrium(demandFun, supplyElast):
	''' program that finds the equilibrium price given the elasticity 
		of supply and a demand function assuming that all goods are
		dumped onto the market at the beginning of the period'''

	def supplyfun(elasticity):

		supply, Q = sym.symbols('supply Q')
		intercept = 0 

		supply = elasticity*Q + intercept
			
		return supply

	supply = supplyfun(supplyElast)

	Q = sym.symbols('Q')

	eqQ = sym.solve(supply - demandFun, Q) 
	# eqP = supply(eqQ) 

	# marketP = demandFun.evalf(subs={Q: quantS})

	return eqQ
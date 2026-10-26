from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

########################################################################################################################

def dummy_geometry(x):
    return 5 #mm
#Im having this dummy function replace what we will get from the geometry team in the future
#dummy_geometry returns a minimum thickness of the airfoil, I have it set to 5mm rn (might be a list of coords later)

def dummy_xfoil_results(x):
    return 44.7, 2.6
# Same here for the Xf0il team, output is a Cl and Cd pair

########################################################################################################################

class Optimizer(ElementwiseProblem): #Elementwise works with a single solution at a time, I think that's what we want?
    def __init__(self):
        super().__init__(n_var = 10, # Number of Bezier points, Bezier points will be our variables
                       n_obj = 1, # Currently just optimizing for Cl/Cd
                       n_ieq_constr = 1, # we are applying one thickness constraint atm
                       xl = 0,
                       xu = 1) # Bezier points should be normalized to the foil, so I'm setting bounds from 0-1
    def _evaluate(self, x, out, *args, **kwargs):
        thickness = dummy_geometry(x)
        Cl, Cd = dummy_xfoil_results(x)
        ld_ratio = Cl/Cd
        out["F"] = -ld_ratio #out["F"] is what we want to optimize, pymoo's algorithymm strictly minimizes instead of maximizes
        out["G"] = 0.8 - thickness #pymoo requires out["G"] <= 0 to pass and out["G"] > 0 to fail. I'm setting 0.8 at min thickness

problem_WW = Optimizer()
NSGA_algo = NSGA2(pop_size=1)
results = minimize(problem_WW, NSGA_algo, n_gen=10)

print("solution: \nX = %s\nF = %s\nG = %s" % (results.X, results.F, results.G))
# X will give you the inputted random values for the problem
# F will give you calculated Cl/Cd
# G will tell you whether thickness passed or failed (neg or pos)

#Test Message
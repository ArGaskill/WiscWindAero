from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

########################################################################################################################

def dummy_geometry(x):
    return {
        "pass": True, #does the geometry pass minimum recommended geometric attributes?
        "dat_file": "airfoil_dat", #imported dat file
        "max_thickness": 1, #normalized thickness
        "te_thickness": .4  #normalized trailing edge thickness
    }
# dummy geometry now returns a dictionary that can give us all the information needed to run the optimizer

def dummy_xfoil_results(x):
    return {
        "Cl_Cd": 42.6, #gives Cl/Cd ratio
        "converged": True, #tells us if the xfoil simulation converged successfully
        "alfa_max": 4 #tells us AOA at max Cl/Cd
    }
# Same here for the Xf0il team

########################################################################################################################

class Optimizer(ElementwiseProblem): #Elementwise works with a single solution at a time, I think that's what we want?
    def __init__(self):
        super().__init__(n_var = 6, # Number of Bezier points, Bezier points will be our variables
                         n_obj = 1, # Currently just optimizing for Cl/Cd
                         n_ieq_constr = 4, #applying max thickness and te thickness, and both booleans
                         xl = [0.08, 0.20, 0.00, 0.25, 0.60, 0.15],
                         xu = [0.20, 0.45, 0.08, 0.60, 1.50, 0.45]) # Bezier points should be normalized to the foil, so I'm setting bounds from 0-1
    def _evaluate(self, x, out, *args, **kwargs):
        geo_data = dummy_geometry(x)
        m_thickness = geo_data["max_thickness"]
        te_thickness = geo_data["te_thickness"]
        geom_pass = geo_data["pass"]

        g1 = 0.8 - m_thickness
        g2 = 0.4 - te_thickness
        g3 = 1 - geom_pass

        dat = geo_data["dat_file"]
        xfoil_data = dummy_xfoil_results(x)
        xfoil_pass = xfoil_data["converged"]
        ld_ratio = xfoil_data["Cl_Cd"]

        g4 = 1 - xfoil_pass

        out["F"] = -ld_ratio #out["F"] is what we want to optimize, pymoo's algorithymm strictly minimizes instead of maximizes
        out["G"] = [g1, g2, g3, g4] #pymoo requires out["G"] <= 0 to pass and out["G"] > 0 to fail.

problem_WW = Optimizer()
NSGA_algo = NSGA2(pop_size=10)
results = minimize(problem_WW, NSGA_algo, termination=('n_gen',10))

print("solution: \nX = %s\nF = %s\nG = %s" % (results.X, results.F, results.G))
# X will give you the inputted random values for the problem
# F will give you calculated Cl/Cd
# G will tell you whether thickness passed or failed (neg or pos) 12

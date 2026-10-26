# WiscWindAero 🌪️

**WiscWindAero** is the main aerodynamics repo for the WiscWind Collegiate Wind Competition team. We are using a multi-objective genetic algorithm (NSGA-II) to optimize our turbine airfoils for maximum aerodynamic efficiency and structural viability within CWC constraints.

## Project Overview

The goal of this framework is to automate the design of our next-generation 4-blade rotors. The code iteratively tweaks blade geometries to minimize the negative Lift-to-Drag ratio by linking modern genetic optimization with the evaluation tools we have used in past years, like QBlade and XFOIL. 

### Core Modules
* **`optimizer.py`**: The main script driving the `pymoo` optimization. It uses the `ElementwiseProblem` class to handle the 10 normalized Bézier control points and enforce our manufacturing constraints.
* **`aerodynamics.py`**: Takes the geometry, runs it through an XFOIL simulation, and pulls the $C_l$ and $C_d$ coefficients needed for the optimization penalty functions.
* **`geometry.py`**: Translates the 10 Bézier control points into a full 2D airfoil geometry format that XFOIL can read.

## Setup & Installation

To run the optimization scripts locally, you must create a virtual environment to isolate the project dependencies. 

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ArGaskill/WiscWindAero.git](https://github.com/ArGaskill/WiscWindAero.git)
   cd WiscWindAero

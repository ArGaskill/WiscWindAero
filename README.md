# WiscWindAero 🌪️

**WiscWindAero** is the primary aerodynamic design and optimization repository for the WiscWind Collegiate Wind Competition team. This framework utilizes a multi-objective genetic algorithm (NSGA-II) to optimize wind turbine airfoil profiles (such as NACA 4412, NACA 6409, and SD7037) for maximum aerodynamic efficiency and structural viability.

## 🚀 Project Overview

The objective of this framework is to iteratively evaluate and optimize turbine blade geometries by minimizing the negative Lift-to-Drag ratio ($-L/D$). It couples modern heuristic optimization with our established evaluation tools (XFOIL and QBlade) to automate the design of our next-generation 4-blade rotor architectures.

### Core Modules
* **`optimizer.py`**: The main execution script running the `pymoo` framework. It utilizes the `ElementwiseProblem` class with 10 normalized design variables (bounded 0 to 1) and enforces manufacturing constraints.
* **`aerodynamics.py`**: Handles aerodynamic evaluations, extracting $C_l$ and $C_d$ coefficients for the optimization penalty functions.
* **`geometry.py`**: Manages spatial coordinates and structural constraints, ensuring strict adherence to the 0.8 mm minimum thickness rule required for our PLA 3D-printing process.

## 🛠️ Setup & Installation

To run the optimization scripts locally, you must create a virtual environment to isolate the project dependencies. 

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ArGaskill/WiscWindAero.git](https://github.com/ArGaskill/WiscWindAero.git)
   cd WiscWindAero

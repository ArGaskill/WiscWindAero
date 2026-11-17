# WiscWindAero 🌪️

**WiscWindAero** is the main aerodynamics repo for the WiscWind Collegiate Wind Competition team. We are using a multi-objective genetic algorithm (NSGA-II) to optimize our turbine airfoils for maximum aerodynamic efficiency and structural viability within CWC constraints.

## Project Overview

The goal of this framework is to automate the design of our next-generation 4-blade rotors. The code iteratively tweaks blade geometries to minimize the negative Lift-to-Drag ratio by linking modern genetic optimization with the evaluation tools we have used in past years, like QBlade and XFOIL. 

### Core Modules
* **`optimizer.py`**: The main script driving the `pymoo` optimization. It uses the `ElementwiseProblem` class to handle the 10 normalized Bézier control points and enforce our manufacturing constraints.
* **`aerodynamics.py`**: Takes the geometry, runs it through an XFOIL simulation, and pulls the $C_l$ and $C_d$ coefficients needed for the optimization penalty functions.
* **`geometry.py`**: Translates the 10 Bézier control points into a full 2D airfoil geometry format that XFOIL can read.

## XFOIL Wrapper (Milestone 1)

`aerodynamics.py` launches the XFOIL executable as a background subprocess and drives it through standard input. It loads the placeholder `airfoils/naca4412.dat`, sets the Reynolds number with `VISC 277000`, and runs an `ASEQ 0 15 1` sweep.

XFOIL itself is not bundled with this repo. Make the executable available in one of these ways:

* add it to `PATH` (or set the `XFOIL_PATH` environment variable), or
* pass `--xfoil C:\path\to\xfoil.exe`.

Run the default sweep:

```bash
python aerodynamics.py
```

Override the airfoil or sweep settings:

```bash
python aerodynamics.py --airfoil airfoils/naca4412.dat --reynolds 277000 --alpha-start 0 --alpha-end 15 --alpha-step 1
```

The parsed polar is printed to the console. The raw `polar.txt`, `xfoil.log`, and copied `airfoil.dat` are kept under `xfoil_runs/<timestamp>/` for debugging.

To call it from Python:

```python
from aerodynamics import run_xfoil

polar = run_xfoil("airfoils/naca4412.dat", reynolds=277_000)
for point in polar.points:
    print(point.alpha, point.cl, point.cd)
```

The wrapper tests use a fake XFOIL executable, so they run without XFOIL installed:

```bash
python -m unittest discover -s tests -v
```

## Setup & Installation

To run the optimization scripts locally, you must create a virtual environment to isolate the project dependencies. 

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/ArGaskill/WiscWindAero.git](https://github.com/ArGaskill/WiscWindAero.git)
   cd WiscWindAero
   ```

## Contacts

* **Arlo Gaskill** — Aerodynamics Lead  
  [agaskill@wisc.edu](mailto:agaskill@wisc.edu)

* **Andrew Hensal** — WiscWind President  
  [ahensal@wisc.edu](mailto:ahensal@wisc.edu)


import subprocess
from pathlib import Path

xfoil_path = r"C:\Users\jacob\Downloads\XFOIL6.99\xfoil.exe"
project_dir = Path(r"C:\Users\jacob\PycharmProjects\WiscWindAero")

# Test airfoil
airfoil_path = project_dir / "Airfoils" / "naca4412.dat"

# Where we want XFOIL to save its results
results_path = project_dir / "Results" / "naca4412_polar.txt"

# Make sure the Results folder exists
results_path.parent.mkdir(exist_ok=True)

# Use a path relative to the project directory
airfoil_relative = airfoil_path.relative_to(project_dir)
results_relative = results_path.relative_to(project_dir)

commands = f"""
LOAD {airfoil_relative}
OPER
VISC 277000
PACC
{results_relative}

ASEQ 0 15 1

"""

process = subprocess.Popen(
    [str(xfoil_path)],
    cwd=str(project_dir),
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = process.communicate(commands)

print(stdout)

if stderr:
    print("ERROR:")
    print(stderr)

print(f"Results saved to: {results_path}")
import numpy as np
import subprocess
from pathlib import Path

xfoil_path = r"xfoil.exe"
project_dir = Path(__file__).resolve().parent
airfoil_path = project_dir / "naca2418.dat"
airfoil_relative = airfoil_path.relative_to(project_dir)
airfoil = "Naca_2418"  # No spaces so XFOIL reads the filename cleanly
reynolds = 277000
iter = 150
start_angle = 0
end_angle = 15
step = 1


def run_xfoil_sweep(airfoil_path, xfoil_path=xfoil_path, airfoil="current", reynolds=277000, iter=150, start_angle=0, end_angle=15, step=1):
    polar_path = project_dir / f"polar_{airfoil}.txt"
    if polar_path.exists():
        polar_path.unlink()  # Delete old polar file before running XFOIL

    commands = [
        f"load {airfoil_path}",
        "pane",
        "oper",
        f"visc {reynolds}",
        f"iter {iter}",
        "pacc",
        f"polar_{airfoil}.txt",
        "",
        f"aseq {start_angle} {end_angle} {step}",
        "pacc",
        "",      # Exit the OPER menu
        "quit",  # Exit XFOIL completely
    ]

    input_commands = "\n".join(commands) + "\n"

    try:
        process = subprocess.Popen(
            [str(xfoil_path)],
            cwd=str(project_dir),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=input_commands, timeout=15)

        # Check if XFOIL created a valid polar file with at least 1 converged row
        if not polar_path.exists():
            return {"Cl_Cd": 0.0, "converged": False, "alfa_max": 0.0}

        data = np.loadtxt(polar_path, skiprows=12)
        if data.size == 0:
            return {"Cl_Cd": 0.0, "converged": False, "alfa_max": 0.0}
        data = np.atleast_2d(data)  # Prevents 1D array crash if only 1 AoA converged

        alpha = data[:, 0]
        cl = data[:, 1]
        cd = data[:, 2]

        division_clcd = cl / cd

        max_clcd = 0.0
        alfa = 0.0

        # enumerate() gives both the exact index (i) and value without off-by-one bugs
        for i, value in enumerate(division_clcd):
            if value > max_clcd:
                max_clcd = float(value)
                alfa = float(alpha[i])

        dictionary = {"Cl_Cd": max_clcd, "converged": True, "alfa_max": alfa}
        return dictionary

    except FileNotFoundError:
        print("Error: XFOIL executable not found.")
        return {"Cl_Cd": 0.0, "converged": False, "alfa_max": 0.0}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"Cl_Cd": 0.0, "converged": False, "alfa_max": 0.0}


if __name__ == "__main__":
    # Argument order now matches def run_xfoil_sweep(airfoil_path, xfoil_path, airfoil, ...)
    result = run_xfoil_sweep(airfoil_relative, xfoil_path, airfoil, reynolds, iter, start_angle, end_angle, step)
    print("\nReturned Dictionary:", result)
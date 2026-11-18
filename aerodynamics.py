import numpy as np
import subprocess
from pathlib import Path

xfoil_path = r"xfoil.exe"
project_dir = Path(__file__).resolve().parent
airfoil_path = project_dir / "airfoil_generated.dat"
airfoil_relative = airfoil_path.relative_to(project_dir)
airfoil = "Naca_2418"
reynolds = 55000
ncrit = 6.5
iter_limit = 200
start_angle = 0
end_angle = 15
step = 0.5


def _failed_result():
    return {
        "Cl_Cd": 0.0,
        "converged": False,
        "alfa_max": 0.0,
        "Max_Cl": 0.0,
        "stall_margin": -10.0,
        "Cl_opt": 0.0,
        "min_slope": -1.0,
    }


def _evaluate_low_re_polar(data: np.ndarray):
    """Extract bubble-resistant low-Re performance metrics from XFOIL polar data."""
    alpha = data[:, 0]
    cl = data[:, 1]
    cd = data[:, 2]

    # Filter out non-physical drag points or negative lift
    valid = (cd > 0.004) & (cl > 0.0)
    if np.sum(valid) < 6:
        return None
    alpha, cl, cd = alpha[valid], cl[valid], cd[valid]
    clcd = cl / cd

    # Restrict design optimum search to practical positive operating angles
    design_mask = (alpha >= 1.0) & (alpha <= 10.0)
    if not np.any(design_mask):
        return None

    design_indices = np.where(design_mask)[0]
    best_local = design_indices[np.argmax(clcd[design_indices])]
    alpha_opt = float(alpha[best_local])
    cl_opt = float(cl[best_local])

    # Windowed Cl/Cd across [alpha_opt - 1.0, alpha_opt + 1.0] to penalize fragile drag buckets
    win = (alpha >= alpha_opt - 1.0) & (alpha <= alpha_opt + 1.0)
    if np.sum(win) < 3:
        return None
    robust_clcd = float(np.mean(clcd[win]))

    # Max Cl and stall margin
    idx_clmax = int(np.argmax(cl))
    max_cl = float(cl[idx_clmax])
    alpha_stall = float(alpha[idx_clmax])
    stall_margin = alpha_stall - alpha_opt

    # Pre-stall lift slope check to detect laminar separation bubble kinks
    pre_stall = alpha <= alpha_stall
    if np.sum(pre_stall) >= 3:
        dcl_da = np.diff(cl[pre_stall]) / np.maximum(np.diff(alpha[pre_stall]), 1e-6)
        min_slope = float(np.min(dcl_da))
    else:
        min_slope = -1.0

    return {
        "Cl_Cd": robust_clcd,
        "converged": True,
        "alfa_max": alpha_opt,
        "Max_Cl": max_cl,
        "stall_margin": stall_margin,
        "Cl_opt": cl_opt,
        "min_slope": min_slope,
    }


def run_xfoil_sweep(
    airfoil_path,
    xfoil_path=xfoil_path,
    airfoil="current",
    reynolds=reynolds,
    ncrit=ncrit,
    iter=iter_limit,
    start_angle=start_angle,
    end_angle=end_angle,
    step=step,
):
    polar_path = project_dir / f"polar_{airfoil}.txt"
    if polar_path.exists():
        polar_path.unlink()  # Delete old polar file before running XFOIL

    commands = [
        "plop",
        "g",
        "",
        f"load {airfoil_path}",
        "pane",
        "oper",
        f"visc {reynolds}",
        "vpar",
        f"n {ncrit}",
        "",
        f"iter {iter}",
        "pacc",
        f"polar_{airfoil}.txt",
        "",
        f"aseq {start_angle} {end_angle} {step}",
        "pacc",
        "",
        "quit",
    ]

    input_commands = "\n".join(commands) + "\n"
    process = None

    try:
        process = subprocess.Popen(
            [str(xfoil_path)],
            cwd=str(project_dir),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=input_commands, timeout=15)

        # Intercept missing or header-only / sparse polar files (header = 12 lines)
        if not polar_path.exists():
            return _failed_result()
        with open(polar_path, "r") as f:
            lines = f.readlines()
        if len(lines) < 18:  # Require at least 6 converged alpha points
            return _failed_result()

        data = np.loadtxt(polar_path, skiprows=12)
        if data.size == 0:
            return _failed_result()
        data = np.atleast_2d(data)

        metrics = _evaluate_low_re_polar(data)
        return metrics if metrics is not None else _failed_result()

    except subprocess.TimeoutExpired:
        if process is not None:
            process.kill()
            process.communicate()
        return _failed_result()

    except FileNotFoundError:
        print("Error: XFOIL executable not found.")
        return _failed_result()

    except Exception as e:
        if process is not None:
            process.kill()
            process.communicate()
        print(f"An unexpected error occurred: {e}")
        return _failed_result()


def run_dual_re_sweep(airfoil_path, re_high=55000, re_low=35000, **kwargs):
    """Blends 70% Re=55k (rated) + 30% Re=35k (mid-tunnel/root) to filter out bubble collapse."""
    res_hi = run_xfoil_sweep(airfoil_path, airfoil="current_hi", reynolds=re_high, **kwargs)
    if not res_hi["converged"]:
        return _failed_result()

    res_lo = run_xfoil_sweep(airfoil_path, airfoil="current_lo", reynolds=re_low, **kwargs)
    if not res_lo["converged"]:
        return _failed_result()

    return {
        "Cl_Cd": 0.70 * res_hi["Cl_Cd"] + 0.30 * res_lo["Cl_Cd"],
        "converged": True,
        "alfa_max": res_hi["alfa_max"],
        "Max_Cl": 0.70 * res_hi["Max_Cl"] + 0.30 * res_lo["Max_Cl"],
        "stall_margin": min(res_hi["stall_margin"], res_lo["stall_margin"]),
        "Cl_opt": res_hi["Cl_opt"],
        "min_slope": min(res_hi["min_slope"], res_lo["min_slope"]),
    }


if __name__ == "__main__":
    result = run_xfoil_sweep(
        airfoil_relative, xfoil_path, airfoil, reynolds, ncrit, iter_limit, start_angle, end_angle, step
    )
    print("\nReturned Dictionary:", result)
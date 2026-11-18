from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from geometry import build_airfoil
from aerodynamics import run_xfoil_sweep, run_dual_re_sweep
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

# ======================= OPTIMIZATION SETTINGS =======================
USE_DUAL_RE = False  # Set True to blend 70% Re=55k + 30% Re=35k (~2x runtime)
POP_SIZE = 12        # Quick sanity check; bump to ~40 for a real run
N_GEN = 5          # Quick sanity check; bump to ~30 for a real run
# =====================================================================


class Optimizer(ElementwiseProblem):
    def __init__(self):
        super().__init__(
            n_var=6,
            n_obj=2,
            n_ieq_constr=8,
            # [T, XT, M, XM, LE_BLUNT, TE_LEN] — thickness bounded to low-Re sweet spot (7.5%–11.5%)
            xl=[0.075, 0.20, 0.00, 0.25, 0.60, 0.15],
            xu=[0.115, 0.45, 0.08, 0.60, 1.50, 0.45],
        )

    def _evaluate(self, x, out, *args, **kwargs):
        geo_data = build_airfoil(x)
        m_thickness = geo_data["max_thickness"]
        te_thickness = geo_data["te_thickness"]
        geom_pass = geo_data["pass"]

        dat = geo_data["dat_file"]
        if USE_DUAL_RE:
            xfoil_data = run_dual_re_sweep(dat)
        else:
            xfoil_data = run_xfoil_sweep(dat)

        xfoil_pass = xfoil_data["converged"]
        ld_ratio = xfoil_data["Cl_Cd"]
        max_cl = xfoil_data["Max_Cl"]
        stall_margin = xfoil_data["stall_margin"]
        cl_opt = xfoil_data["Cl_opt"]
        min_slope = xfoil_data["min_slope"]

        # Constraints (all must be <= 0 to be feasible)
        g1 = 0.075 - m_thickness    # t/c >= 7.5% (>= 1.43 mm at 19 mm tip)
        g2 = m_thickness - 0.115    # t/c <= 11.5% (avoids thick-foil LSB drag)
        g3 = 0.004 - te_thickness   # TE gap >= 0.4% chord
        g4 = 1 - int(geom_pass)     # Valid geometry
        g5 = 1 - int(xfoil_pass)    # Converged XFOIL polar (>= 6 points)
        g6 = 3.0 - stall_margin     # At least 3.0 deg margin before stall
        g7 = 0.70 - cl_opt          # Keeps Schmitz chord compact
        g8 = 0.01 - min_slope       # Rejects pre-stall separation bubble lift drops

        out["F"] = [-ld_ratio, -max_cl]
        out["G"] = [g1, g2, g3, g4, g5, g6, g7, g8]


problem_WW = Optimizer()
NSGA_algo = NSGA2(pop_size=POP_SIZE)
results = minimize(problem_WW, NSGA_algo, termination=("n_gen", N_GEN), seed=1, verbose=True)

if results.X is not None:
    F = np.atleast_2d(-results.F)
    X = np.atleast_2d(results.X)

    idx_best_clcd = np.argmax(F[:, 0])
    idx_best_lift = np.argmax(F[:, 1])

    print("\n--- RESULTS (Re = 55k Low-Re Tunnel) ---")

    print("Highest Robust Cl/Cd:")
    print(f"   Robust Cl/Cd: {F[idx_best_clcd, 0]:.2f}")
    print(f"   Max Cl:       {F[idx_best_clcd, 1]:.3f}")
    print(f"   Parameters:   {np.round(X[idx_best_clcd], 4)}\n")

    print("Highest Lift:")
    print(f"   Robust Cl/Cd: {F[idx_best_lift, 0]:.2f}")
    print(f"   Max Cl:       {F[idx_best_lift, 1]:.3f}")
    print(f"   Parameters:   {np.round(X[idx_best_lift], 4)}\n")

    # Safe min-max normalization (avoids division by zero if only 1 feasible point)
    clcd_span = max(float(np.ptp(F[:, 0])), 1e-9)
    lift_span = max(float(np.ptp(F[:, 1])), 1e-9)
    norm_clcd = (F[:, 0] - np.min(F[:, 0])) / clcd_span
    norm_lift = (F[:, 1] - np.min(F[:, 1])) / lift_span

    distances = np.sqrt((1.0 - norm_clcd) ** 2 + (1.0 - norm_lift) ** 2)
    idx_balanced = int(np.argmin(distances))

    print("Balanced Mid-Span:")
    print(f"   Robust Cl/Cd: {F[idx_balanced, 0]:.2f}")
    print(f"   Max Cl:       {F[idx_balanced, 1]:.3f}")
    print(f"   Parameters:   {np.round(X[idx_balanced], 4)}\n")

    # Export champion .dat files with Re55k tag
    build_airfoil(X[idx_best_clcd], filename="WW_Max_ClCd_Re55k.dat")
    build_airfoil(X[idx_best_lift], filename="WW_Max_Lift_Re55k.dat")
    build_airfoil(X[idx_balanced], filename="WW_MidSpan_Balanced_Re55k.dat")

    data = {
        "Lift": F[:, 1],
        "ClCd": F[:, 0],
        "Thickness": X[:, 0],
    }
    parameters = [str(np.round(x, 4)) for x in X]

    fig = px.scatter(
        data,
        x="Lift",
        y="ClCd",
        color="Thickness",
        hover_name=parameters,
        title="WiscWind Pareto Front (Re = 55k, N-Crit = 6.5)",
    )
    fig.add_trace(
        go.Scatter(
            x=[F[idx_best_clcd, 1], F[idx_best_lift, 1], F[idx_balanced, 1]],
            y=[F[idx_best_clcd, 0], F[idx_best_lift, 0], F[idx_balanced, 0]],
            mode="markers+text",
            marker=dict(
                symbol="star",
                size=16,
                color="#c5050c",
                line=dict(width=2, color="black"),
            ),
            text=["Efficiency Champion", "Lift Champion", "Balanced Champion"],
            textposition="top center",
            name="Champions",
            hoverinfo="skip",
        )
    )

    fig.show()
    fig.write_html("WW_Pareto_Front_Re55k.html")
else:
    print("No feasible airfoils found. Try increasing POP_SIZE / N_GEN or relaxing g6/g8 slightly.")
"""
Generic parametric Bezier airfoil

Build the airfoil from two small Bezier curves that share the SAME x control
points:
    thickness curve  yt(t)  -> half-thickness distribution
    camber curve     yc(t)  -> camber line
    upper surface = (x(t), yc(t) + yt(t))
    lower surface = (x(t), yc(t) - yt(t))


Control points run LE -> TE, 6 per surface (degree 5).
"""
import math
import numpy as np
import matplotlib.pyplot as plt

# ======================= DESIGN CONSTANTS =======================
N = 5   # Bezier degree (N + 1 = 6 control points)
tt = np.linspace(0, 1, 4001)    # dense parameter grid used for measuring
TE_GAP   = 0.004    # trailing-edge thickness, fraction of chord (0 = sharp)
CHORD    = 1.0    # chord length used for the exported file
# ==============================================================================

def bernstein_matrix(n, t):
    """Rows = parameter values, columns = basis functions B_{i,n}(t)."""
    t = np.atleast_1d(t)
    return np.array([math.comb(n, i) * t**i * (1 - t)**(n - i)
                     for i in range(n + 1)]).T


def bezier(ctrl, t):
    """Evaluate a Bezier curve. ctrl can be (k,) for 1-D or (k, 2) for x-y."""
    ctrl = np.asarray(ctrl, float)
    return bernstein_matrix(len(ctrl) - 1, t) @ ctrl


def build_airfoil(a):
    T, XT, M, XM, LE_BLUNT, TE_LEN = a #The 6 design parameters the airfoil will be modeled from

    x2 = 0.05                      # sets how fast the nose opens up
    x4 = 1.0 - TE_LEN
    h = 0.375 * math.sqrt(LE_BLUNT) # thickness heights relative to the peak (peak = 1). Index 1 sets the nose.
    raw = np.array([0.0, h, 0.85, 1.0, 1.0, 0.0])

    # Move control point 3 so the thickness peak lands at x = XT.
    t_pk = tt[np.argmax(bezier(raw, tt))]   # x(t*) is linear in X[3], so this is solved directly (no iteration).
    B = bernstein_matrix(N, t_pk)[0]
    rest = B @ np.array([0.0, 0.0, x2, 0.0, x4, 1.0])
    x3 = np.clip((XT - rest) / B[3], x2, x4)
    X = np.array([0.0, 0.0, x2, x3, x4, 1.0])

    # ---- scale thickness so the measured max thickness equals T ----
    g = TE_GAP / 2.0
    def half_thickness(s):
        y = s * raw
        y[5] = g
        return y

    s = T / 2.0
    for _ in range(30):
        s *= (T / 2.0) / bezier(half_thickness(s), tt).max()
    yt = half_thickness(s)

    # ---- camber: bump of control heights, tuned so the peak lands at x = XM ----
    c = np.zeros(6)
    if M > 0:
        t_m = np.interp(XM, bezier(X, tt), tt)      # parameter value where x = XM
        centre, width = t_m, 0.25
        idx = np.array([2, 3, 4]) / N
        for _ in range(60):
            c[2:5] = np.exp(-((idx - centre) / width) ** 2)
            t_peak = tt[np.argmax(bezier(c, tt))]
            centre = np.clip(centre + 0.8 * (t_m - t_peak), 0.0, 1.0)
        c *= M / bezier(c, tt).max()

    upper = np.c_[X, c + yt]
    lower = np.c_[X, c - yt]

    filename = "airfoil_generated.dat"

    # Evaluate 80 points per surface (159 total points in Selig order)
    t_export = np.linspace(0, 1, 80)
    cu, cl = bezier(upper, t_export), bezier(lower, t_export)

    # TE upper -> LE -> TE lower (cl[1:] avoids duplicating the (0,0) nose point)
    pts = np.vstack([cu[::-1], cl[1:]]) * CHORD

    with open(filename, "w") as f:
        f.write("Bezier_Airfoil\n")
        np.savetxt(f, pts, fmt="%.6f")

    return {
        "pass": True,
        "dat_file": filename,
        "max_thickness": float(T),
        "te_thickness": float(TE_GAP),
        "upper": upper,
        "lower": lower
    }

if __name__ == "__main__":
    #test run (only executes when running geometry.py directly)
    sample_params = [0.1898, 0.3568, 0.0680, 0.3527, 1.2128, 0.4155]
    res = build_airfoil(sample_params)
    upper, lower = res["upper"], res["lower"]

    t = np.linspace(0, 1, 80)
    cu, cl = bezier(upper, t), bezier(lower, t)
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.fill(np.r_[cu[:, 0], cl[::-1, 0]], np.r_[cu[:, 1], cl[::-1, 1]],
            color="#cfe3f5", alpha=0.6)
    ax.plot(*cu.T, "r", lw=2, label="Bezier surfaces")
    ax.plot(*cl.T, "r", lw=2)
    ax.plot(*upper.T, "o--", color="gray", ms=5, lw=0.8, label="Control polygons")
    ax.plot(*lower.T, "o--", color="gray", ms=5, lw=0.8)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    plt.show()

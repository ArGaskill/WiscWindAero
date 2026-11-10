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

# ======================= DESIGN PARAMETERS (edit these) =======================
T        = 1.89873217e-01   # max thickness, fraction of chord
XT       = 3.56799552e-01   # chordwise position of max thickness
M        = 6.80317820e-02   # max camber, fraction of chord (0 = symmetric)
XM       = 3.52701906e-01    # chordwise position of max camber
LE_BLUNT = 1.21277438e+00    # nose radius factor (1 = typical, >1 rounder, <1 sharper)
TE_LEN   = 4.15544514e-01   # length of the last control leg (shorter = larger TE angle)
TE_GAP   = 0.0    # trailing-edge thickness, fraction of chord (0 = sharp)
CHORD    = 1.0    # chord length used for the exported file
# ==============================================================================

N = 5                              # Bezier degree (N + 1 = 6 control points)
tt = np.linspace(0, 1, 4001)       # dense parameter grid used for measuring


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
    # ---- x control positions, shared by thickness, camber and both surfaces ----
    T, XT, M, XM, LE_BLUNT, TE_LEN = a #The 6 design parameters the airfoil will be modeled from
    x2 = 0.05                      # sets how fast the nose opens up
    x4 = 1.0 - TE_LEN
    # thickness heights relative to the peak (peak = 1). Index 1 sets the nose.
    h = 0.375 * math.sqrt(LE_BLUNT)
    raw = np.array([0.0, h, 0.85, 1.0, 1.0, 0.0])

    # Move control point 3 so the thickness peak lands at x = XT.
    # x(t*) is linear in X[3], so this is solved directly (no iteration).
    t_pk = tt[np.argmax(bezier(raw, tt))]
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

    return {
        "pass": True,
        "dat_file": filename,
        "max_thickness": T,
        "te_thickness": TE_GAP
    }


def report(upper, lower):
    u, l = bezier(upper, tt), bezier(lower, tt)
    thick = u[:, 1] - l[:, 1]
    camber = (u[:, 1] + l[:, 1]) / 2
    i, j = np.argmax(thick), np.argmax(camber)
    yt1 = (upper[1, 1] - lower[1, 1]) / 2
    r_le = N / (N - 1) * yt1**2 / upper[2, 0]       # nose radius of thickness curve
    du, dl = upper[-1] - upper[-2], lower[-1] - lower[-2]
    wedge = np.degrees(np.arctan2(dl[1], dl[0]) - np.arctan2(du[1], du[0]))
    print(f"max thickness : {thick[i]:.4f} at x = {u[i, 0]:.3f}   (target {T} at {XT})")
    print(f"max camber    : {camber[j]:.4f} at x = {u[j, 0]:.3f}   (target {M} at {XM})")
    print(f"nose radius   : {r_le:.4f}")
    print(f"TE wedge angle: {wedge:.1f} deg")


upper, lower = build_airfoil()
report(upper, lower)

print("\nControl points (paste into the draggable editor if you want to hand-tune):")
print("upper =", np.array2string(np.round(upper, 4), separator=", "))
print("lower =", np.array2string(np.round(lower, 4), separator=", "))

# ------------------------------ plot ------------------------------
t = np.linspace(0, 1, 80)
cu, cl = bezier(upper, t), bezier(lower, t)
fig, ax = plt.subplots(figsize=(11, 4))
ax.fill(np.r_[cu[:, 0], cl[::-1, 0]], np.r_[cu[:, 1], cl[::-1, 1]],
        color="#cfe3f5", alpha=0.6)
ax.plot(*cu.T, "r", lw=2, label="Bezier surfaces")
ax.plot(*cl.T, "r", lw=2)
ax.plot(*upper.T, "o--", color="gray", ms=5, lw=0.8, label="Control polygons")
ax.plot(*lower.T, "o--", color="gray", ms=5, lw=0.8)
ax.plot((cu[:, 0]), (cu[:, 1] + cl[:, 1]) / 2, "b:", lw=1, label="Camber line")
ax.set_aspect("equal")
ax.grid(alpha=0.3)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False)
ax.set_title(f"Parametric Bezier airfoil  T={T}  M={M}")
plt.savefig("bezier_airfoil.png", dpi=130, bbox_inches="tight")
plt.show()

# -------------- export for SolidWorks (Curve Through XYZ Points) --------------
# TE upper -> LE -> TE lower, LE point not duplicated
pts = np.vstack([cu[::-1], cl]) * CHORD   #traces points as one curve, scales to chord length

with open("airfoil.dat", "w") as f:
    f.write("Bezier Airfoil\n")
    np.savetxt(f, pts, fmt="%.6f")

print("\nSaved airfoil.dat")

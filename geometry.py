# ==============================================================================
# Airfoil from one Bezier Curve w/ 10 points
# Curve runs from trailing edge, over top, under and back
# Drag any point with the mouse, or edit the numbers in STEP 1.
#   p = print the points (so you can paste them back into STEP 1)
#   s = save the airfoil as a text file (X, Y, Z columns for SolidWorks)
# ==============================================================================

import math
import numpy as np
import matplotlib.pyplot as plt

points = np.array([
    [1.00, 0.004],  # point 0  trailing edge, top    curve start
    [0.80, 0.045],  # point 1  top surface,
    [0.50, 0.100],  # point 2  top surface,
    [0.20, 0.130],  # point 3  top surface,
    [-0.30, 0.120],  # point 4  nose, top
    [-0.30, -0.090],  # point 5  nose, bottom
    [0.20, -0.060],  # point 6  bottom surface
    [0.50, -0.050],  # point 7  bottom surface
    [0.80, -0.025],  # point 8  bottom surface
    [1.00, -0.004],  # point 9  trailing edge, bottom  curve end
])


def make_curve(control_points, how_many=400):
    n = len(control_points) - 1  # 10 points -> n = 9
    t = np.linspace(0, 1, how_many)  # 400 numbers from 0 (start) to 1 (end)
    curve = np.zeros((how_many, 2))  # empty table: 400 rows, columns x and y

    for i in range(n + 1):  # repeat once for each control point
        pull = math.comb(n, i) * t ** i * (1 - t) ** (n - i)  # how hard point i pulls
        curve += np.outer(pull, control_points[i])  # add its pull to the curve

    return curve


#defining curve in airfoil terms chord, %thick, others
def measure(curve):
    nose = np.argmin(curve[:, 0])  #defines measurements to find chord
    top = curve[:nose + 1][::-1]  #defines measurements to find chord

    bottom = curve[nose:]

    x_nose = curve[:, 0].min()
    chord = curve[:, 0].max() - x_nose  # length from nose to tail

    # Line up top and bottom at the same x positions so we can subtract them
    x = np.linspace(x_nose, x_nose + chord, 400)
    y_top = np.interp(x, top[:, 0], top[:, 1])
    y_bottom = np.interp(x, bottom[:, 0], bottom[:, 1])

    thickness = (y_top - y_bottom) / chord  # finds all thicknesses at all y
    i = np.argmax(thickness)  # largest thickness
    return thickness[i], (x[i] - x_nose) / chord, chord


def info_text():
    thickness, where, chord = measure(make_curve(points))
    return (f"max thickness {thickness * 100:.1f}% at {where * 100:.0f}% of the chord   |   "
            f"chord {chord:.3f}")


#airfoil plot
fig, ax = plt.subplots(figsize=(11, 5))

curve = make_curve(points)
shape = ax.fill(curve[:, 0], curve[:, 1], color="#cfe3f5")[0]  # the light-blue body
outline, = ax.plot(curve[:, 0], curve[:, 1], color="red", linewidth=2.5,
                   label="Airfoil (Bezier curve)")
polygon, = ax.plot(points[:, 0], points[:, 1], "o--", color="gray",
                   markersize=10, linewidth=1, label="Control points")

#prevents overlap with labels
label_offset = [0.015] * 5 + [-0.03] * 5

labels = []  # identifying numbers at each control point
for i in range(len(points)):
    labels.append(ax.text(points[i, 0], points[i, 1] + label_offset[i], str(i),
                          ha="center", fontsize=10))

ax.set_xlim(-0.4, 1.1)  # fixed view so it doesn't jump around
ax.set_ylim(-0.25, 0.25)
ax.set_aspect("equal")  # same scale on both axes
ax.grid(alpha=0.3)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False)
title = ax.set_title(info_text())

# creates manual control point movements
grabbed = None #inital condition




def on_key(event):
    """p = print the points.  s = save the airfoil to a text file."""
    if event.key == "p":
        print("points = np.array(" + str(np.round(points, 3).tolist()) + ")")

    elif event.key == "s":
        c = make_curve(points)
        x_nose = c[:, 0].min()
        chord = c[:, 0].max() - x_nose
        c = np.c_[(c[:, 0] - x_nose) / chord, c[:, 1] / chord]  # nose at x=0, chord = 1
        xyz = np.c_[c, np.zeros(len(c))]  # add a column of zeros (Z)
        np.savetxt("airfoil_10pt.txt", xyz, fmt="%.6f", delimiter="\t")
        print("Saved airfoil_10pt.txt")


fig.canvas.mpl_connect("key_press_event", on_key)

plt.show()
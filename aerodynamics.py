import numpy as np
import subprocess
from pathlib import Path

xfoil_path = r"xfoil.exe"
project_dir = Path(r"C:\Users\jacob\PycharmProjects\WiscWindAero") ##chage to your filepath
airfoil_path = project_dir / "naca2418.dat"
airfoil_relative = airfoil_path.relative_to(project_dir)
airfoil = "Naca 2418"
reynolds = 277000
iter = 150
start_angle = 0
end_angle = 15
step = 1


def run_xfoil_sweep(airfoil, xfoil_path, airfoil_path, reynolds, iter, start_angle, end_angle, step):
  # Define the sequence of commands to send to XFOIL's interactive prompt.
  # Empty strings ("") simulate pressing the Enter key to accept defaults or prompts.
  commands = [
      f"load {airfoil_path}",  # Load the input dat file
      "",  # Press Enter if prompted for name/modifications
      "oper",  # Enter the OPERating menu
      f"visc {reynolds}",  # Set viscous mode with Reynolds number
      f"iter {iter}",  # (Optional) Increase max iterations for convergence safety
      "pacc",  # Turn on polar accumulation
      f"polar_{airfoil}.txt",  # Name of the output polar file
      "",  # Dump file name (leave blank to skip)
      f"aseq {start_angle} {end_angle} {step}",  # Run Angle of Attack sequence from 0 to 15 with step 1
      "pacc",  # Turn off polar accumulation
      "quit",  # Exit the OPER menu
      "quit",  # Exit XFOIL completely
  ]

  # Join commands into a single multi-line string separated by newlines
  input_commands = "\n".join(commands) + "\n"

  try:
    print("Starting XFOIL subprocess...")

    # Launch XFOIL in the background
    process = subprocess.Popen(
        [str(xfoil_path)],
        cwd=str(project_dir),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    # Send the commands to XFOIL and capture the output and errors
    stdout, stderr = process.communicate(input=input_commands)

    print("XFOIL execution finished successfully!")
    print("\n--- XFOIL Output Log ---")
    print(stdout)

    if stderr:
      print("\n--- Errors / Warnings ---")
      print(stderr)

  except FileNotFoundError:
    print(
        "Error: XFOIL executable not found. Make sure XFOIL is installed and"
        " added to your system PATH, or provide its absolute path."
    )
  except Exception as e:
    print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
  polar_path = project_dir / f"polar_{airfoil}.txt"
  if polar_path.exists():
     polar_path.unlink()  # Deletes the old polar file
  run_xfoil_sweep(airfoil, xfoil_path, airfoil_relative, reynolds, iter, start_angle, end_angle, step)
  data = np.loadtxt(f"polar_{airfoil}.txt", skiprows=12)

  # extracts the values in the polar text file, creating an array
  alpha = data[:, 0]
  cl = data[:, 1]
  cd = data[:, 2]
  CDp = data[:, 3]
  CM = data[:, 4]
  Top_Xtr = data[:, 5]
  Bot_Xtr = data[:, 6]

  division_clcd = cl / cd  # divides the cl value by the cd value to get the cl/cd ratio, puts the values in an array
  print(division_clcd)  # prints the array

  max = 0  # sets variable "max" to 0

  # for loop to find the max value in the division_clcd array
  for value in division_clcd:
      if value > max:
          max = value

  print(f"\nThis is the max cl/cd:  {max}")



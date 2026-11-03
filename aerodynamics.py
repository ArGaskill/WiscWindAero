

import subprocess
from pathlib import Path

xfoil_path = r"C:\Users\jacob\Downloads\XFOIL6.99\xfoil.exe"
project_dir = Path(r"C:\Users\jacob\PycharmProjects\WiscWindAero")
airfoil_path = project_dir / "Airfoils" / "naca4412.dat"
airfoil_relative = airfoil_path.relative_to(project_dir)

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
      f"visc {reynolds}",  # Set viscous mode with Reynolds number 277,000
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
  run_xfoil_sweep("Naca 4412", xfoil_path, airfoil_relative, reynolds, iter, start_angle, end_angle, step)

  # import subprocess
  # from pathlib import Path
  #
  # xfoil_path = r"C:\Users\jacob\Downloads\XFOIL6.99\xfoil.exe"
  # project_dir = Path(r"C:\Users\jacob\PycharmProjects\WiscWindAero")
  #
  # # Test airfoil
  # airfoil_path = project_dir / "Airfoils" / "naca4412.dat"
  #
  # # Where we want XFOIL to save its results
  # results_path = project_dir / "Results" / "naca4412_polar.txt"
  #
  # # Make sure the Results folder exists
  # results_path.parent.mkdir(exist_ok=True)
  #
  # # Use a path relative to the project directory
  # airfoil_relative = airfoil_path.relative_to(project_dir)
  # results_relative = results_path.relative_to(project_dir)
  #
  # commands = f"""
  # LOAD {airfoil_relative}
  # OPER
  # VISC 277000
  # PACC
  # {results_relative}
  #
  # ASEQ 0 15 1
  #
  # """
  #
  # process = subprocess.Popen(
  #     [str(xfoil_path)],
  #     cwd=str(project_dir),
  #     stdin=subprocess.PIPE,
  #     stdout=subprocess.PIPE,
  #     stderr=subprocess.PIPE,
  #     text=True
  # )
  #
  # stdout, stderr = process.communicate(commands)
  #
  # print(stdout)
  #
  # if stderr:
  #     print("ERROR:")
  #     print(stderr)
  #
  # print(f"Results saved to: {results_path}")
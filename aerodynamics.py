import subprocess


def run_xfoil_sweep():
  # Define the sequence of commands to send to XFOIL's interactive prompt.
  # Empty strings ("") simulate pressing the Enter key to accept defaults or prompts.
  commands = [
      "load naca4412.dat",  # Load the placeholder NACA 4412 .dat file
      "",  # Press Enter if prompted for name/modifications
      "oper",  # Enter the OPERating menu
      "visc 277000",  # Set viscous mode with Reynolds number 277,000
      "iter 150",  # (Optional) Increase max iterations for convergence safety
      "pacc",  # Turn on polar accumulation
      "polar_naca4412.txt",  # Name of the output polar file
      "",  # Dump file name (leave blank to skip)
      "aseq 0 15 1",  # Run Angle of Attack sequence from 0 to 15 with step 1
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
        ["xfoil"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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
  run_xfoil_sweep()



"""
MAIN FILE
This is what the system executes, calling the runApp function within the GUI.

Program flow is as follows:

Run GUI to collect user settings and preferences

After settings collected, launch additional thread to compute and evaluate siRNAs

(During this process the preogram must launch two subprocess for RNA folding, which is why python is required for the machine on this version)

The backend thread then returns the results to the GUI


"""

import subprocess
import sys
import os


# Add the parent directory of `Main_Files` to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from Main_Files.GUI import *


def check_python_installation():
    """Check if Python is installed and available in the PATH."""
    try:
        # Attempt to call 'python --version' to check if Python is installed
        result = subprocess.run(
            ["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            raise FileNotFoundError("Python not found.")

        return True

    except FileNotFoundError:
        # Show the error message in a console window
        error_message = "Python is not installed or not available in the PATH. Please install Python and add it to your PATH."
        open_console_with_message(error_message)
        return False


def open_console_with_message(message):
    """Open a new console window with an error message."""
    # Create a simple batch file that opens a console and shows the error message
    batch_script = f"""
    @echo off
    echo {message}
    pause
    exit
    """
    # Save the batch script to a temporary file
    with open("error_message.bat", "w") as f:
        f.write(batch_script)

    # Run the batch file to open a console window
    os.system("start cmd /c error_message.bat")


if __name__ == "__main__":
    # Check for Python installation and show error in a console if not found
    if not check_python_installation():
        print("Please install Python and ensure it's added to your system's PATH.")
    else:
        runApp()

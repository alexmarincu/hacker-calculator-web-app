import os
import sys
import subprocess

VENV_DIR = ".pyvenv"
PYTHON_EXEC = sys.executable


def runCommand(command):
    result = subprocess.run(command, shell=True, check=True)
    return result.returncode


def createVenv():
    if not os.path.exists(VENV_DIR):
        print(f"Creating virtual environment in {VENV_DIR}...")
        runCommand(f"{PYTHON_EXEC} -m venv {VENV_DIR}")


def installRequirements():
    pip_exec = os.path.join(VENV_DIR, "bin", "pip")
    runCommand(f"{pip_exec} install --upgrade pip")

    if os.path.exists("requirements.txt"):
        print("Installing dependencies from requirements.txt...")
        runCommand(f"{pip_exec} install -r requirements.txt")


if __name__ == "__main__":
    createVenv()
    installRequirements()
    print("Virtual environment setup complete.")

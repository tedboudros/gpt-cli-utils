import subprocess
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: gcu <util_name> [arguments...]")
        # print all files inside the utils directory
        print("-"*80)
        print("Available utilities:")
        for file in os.listdir(os.path.join(os.path.dirname(__file__), 'utils')):
            if file.endswith('.py'):
                print(f" - {file[:-3]}")
        return

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    # Append .py extension to the script name
    script_name_with_extension = "./utils/" + script_name + '.py'
    script_path = os.path.join(os.path.dirname(__file__), script_name_with_extension)

    if not os.path.isfile(script_path):
        print(f"Script '{script_name_with_extension}' not found in the current directory.")
        return

    # Check if virtual environment exists
    venv_path = os.path.join(os.path.dirname(__file__), 'venv')
    if not os.path.isdir(venv_path):
        print("Virtual environment 'venv' not found in the current directory.")
        return

    # Determine the path to the Python interpreter in the virtual environment
    if os.name == 'nt':  # Windows
        python_executable = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:  # Unix or MacOS
        python_executable = os.path.join(venv_path, 'bin', 'python')

    if not os.path.isfile(python_executable):
        print("Python executable not found in the virtual environment.")
        return

    # Construct the command to run the target script with arguments
    command = [python_executable, script_path] + script_args

    # Run the command
    result = subprocess.run(command, text=True)

    if result.returncode != 0:
        print(f"Script '{script_name_with_extension}' exited with an error: {result.returncode}")

if __name__ == "__main__":
    main()

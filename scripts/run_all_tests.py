#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

workspace_folder = Path(__file__).parent.parent.absolute()

pythonpath_additions = [
   str(workspace_folder / "model" / "src"),
   str(workspace_folder / "services" / "src")
]

test_dirs = [
   str(workspace_folder / "model" / "tests"),
   str(workspace_folder / "services" / "tests")
]

def run_all_tests():
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")

    if existing_pythonpath:
        pythonpath_additions.append(existing_pythonpath)
    
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_additions)
    
    cmd = [
        sys.executable, "-m", "pytest",
        *test_dirs,
        "-v"
    ]
    
    print("Running all tests...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {workspace_folder}")
    print(f"PYTHONPATH: {env['PYTHONPATH']}")
    print("-" * 50)
    
    try:
        # Run pytest with the specified arguments
        result = subprocess.run(
            cmd,
            cwd=workspace_folder,
            env=env,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Return the exit code
        return result.returncode
        
    except FileNotFoundError:
        print("Error: pytest not found. Make sure it's installed.")
        print("Install with: pip install pytest")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
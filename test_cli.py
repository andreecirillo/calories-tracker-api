import subprocess
import sys
import os

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return False
    return True

def main():
    # Check if database exists
    db_file = 'calories.db'
    if not os.path.exists(db_file):
        print(f"Database file {db_file} not found. Running import_data.py...")
        if not run_command(f"{sys.executable} import_data.py"):
            print("Failed to import data.")
            return
    
    # Test CLI commands
    print("\n=== Testing CLI Commands ===")
    
    print("\n1. Adding a test entry...")
    if not run_command(f"{sys.executable} main.py add-entry --user-id 999 --username test_user --food-name \"Test Food\" --calories 500"):
        print("Failed to add test entry.")
    
    print("\n2. Listing recent entries...")
    if not run_command(f"{sys.executable} main.py list-entries --username test_user"):
        print("Failed to list entries.")
    
    print("\n3. Listing entries for unhealthy_user...")
    if not run_command(f"{sys.executable} main.py list-entries --username unhealthy_user"):
        print("Failed to list unhealthy_user entries.")

if __name__ == "__main__":
    main()

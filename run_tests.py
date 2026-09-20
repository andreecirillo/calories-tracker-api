import subprocess
import sys
import time
import requests

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def test_api():
    # Start the FastAPI server in the background
    server = subprocess.Popen(
        [sys.executable, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Give the server some time to start
        time.sleep(3)
        
        # Test GET /api/entries/
        print("\nTesting GET /api/entries/")
        response = requests.get("http://localhost:8000/api/entries/")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()[:2]}... (truncated)" if response.status_code == 200 else response.text)
        
        # Test POST /api/entries/
        print("\nTesting POST /api/entries/")
        test_data = {
            "user_id": 1,
            "username": "test_user",
            "food_name": "Test Food",
            "calories": 500,
            "date_time": "2025-05-20T12:00:00"
        }
        response = requests.post("http://localhost:8000/api/entries/", json=test_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}" if response.status_code == 201 else response.text)
        
    finally:
        # Stop the server
        server.terminate()
        server.wait()

def main():
    print("=== Setting up the environment ===")
    
    # Install dependencies
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        sys.exit(1)
    
    print("\n=== Importing sample data ===")
    if not run_command(f"{sys.executable} import_data.py"):
        sys.exit(1)
    
    print("\n=== Testing the API ===")
    test_api()
    
    print("\n=== Setup and testing completed successfully! ===")
    print("\nTo start the server, run:")
    print("    python run.py")
    print("\nThen access the API documentation at:")
    print("    http://localhost:8000/docs")

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Quick start script for the Customer Registry API."""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Failed: {description}")
        return False
    print(f"Success: {description}")
    return True


def main():
    """Run the startup sequence."""
    print("\n" + "="*60)
    print("  Customer Registry API - Startup")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Python 3.9+ required")
        return 1
    
    print(f"✓ Python {sys.version.split()[0]}")
    
    # Check/create .env file
    if not os.path.exists(".env"):
        print("Creating .env from .env.example")
        with open(".env.example") as src, open(".env", "w") as dst:
            dst.write(src.read())
    else:
        print(".env file exists")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return 1
    
    # Run tests
    print("\nRunning tests...")
    test_result = subprocess.run(
        "pytest tests/ -v --tb=short",
        shell=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    
    if test_result.returncode != 0:
        print("Some tests failed. Review output above.")
    else:
        print("\n✓ All tests passed!")
    
    # Start the server
    print("\n" + "="*60)
    print("  Starting API Server")
    print("="*60)
    print("Server running at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/api/docs")
    print("Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        subprocess.run(
        [
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        check=True,
    )
    except KeyboardInterrupt:
        print("\nServer stopped.")
    #os.system("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


import argparse
import subprocess
import sys

# Gets the exact python binary currently running this script
python_bin = sys.executable

def run_server():
    print("Starting FastAPI Server...")
    subprocess.run([python_bin, "-m", "uvicorn", "robotdegilim_xyz_backend.main:app", "--reload"])

def run_worker():
    print("Starting Background Worker...")
    subprocess.run([python_bin, "-m", "robotdegilim_xyz_backend.worker.main"])

def run_both():
    print("Starting BOTH Server and Worker...")
    server_process = subprocess.Popen([python_bin, "-m", "uvicorn", "robotdegilim_xyz_backend.main:app", "--reload"])
    worker_process = subprocess.Popen([python_bin, "-m", "robotdegilim_xyz_backend.worker.main"])
    
    try:
        server_process.wait()
        worker_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down both processes...")
        server_process.terminate()
        worker_process.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RobotDegilim Runner")
    parser.add_argument("mode", choices=["server", "worker", "all"], help="Choose what to run")
    args = parser.parse_args()

    if args.mode == "server":
        run_server()
    elif args.mode == "worker":
        run_worker()
    elif args.mode == "all":
        run_both()

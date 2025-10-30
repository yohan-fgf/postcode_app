#!/usr/bin/env python3
"""
Run both aged_care_postcode_app and ndis_postcode_app concurrently.
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Run both apps in parallel."""
    # Define the scripts to run
    scripts = [
        'src/aged_care_postcode_app.py',
        'src/ndis_postcode_app.py'
    ]
    
    # Check if scripts exist
    repo_dir = Path(__file__).parent
    for script in scripts:
        script_path = repo_dir / script
        if not script_path.exists():
            print(f"Error: {script} not found in {repo_dir}")
            sys.exit(1)
    
    print("Starting both applications...")
    print("-" * 50)
    
    # Start both processes
    processes = []
    try:
        for script in scripts:
            print(f"Launching {script}...")
            process = subprocess.Popen(
                [sys.executable, script],
                cwd=repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            processes.append((script, process))
        
        print("-" * 50)
        print("Both applications are running. Press Ctrl+C to stop all.\n")
        
        # Monitor processes and stream output
        import select
        while processes:
            for script, process in processes[:]:
                # Check if process has output
                if process.stdout and select.select([process.stdout], [], [], 0)[0]:
                    line = process.stdout.readline()
                    if line:
                        print(f"[{script}] {line.rstrip()}")
                
                # Check if process has terminated
                retcode = process.poll()
                if retcode is not None:
                    print(f"\n{script} exited with code {retcode}")
                    processes.remove((script, process))
        
    except KeyboardInterrupt:
        print("\n\nShutting down applications...")
        for script, process in processes:
            process.terminate()
            print(f"Terminated {script}")
        
        # Wait for processes to terminate
        for script, process in processes:
            process.wait(timeout=5)
        
        print("All applications stopped.")
    
    except Exception as e:
        print(f"Error: {e}")
        for script, process in processes:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
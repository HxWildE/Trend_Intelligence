import schedule
import sys
import time
import subprocess
import os
from datetime import datetime

# 🔹 Paths to your existing scripts
# We use absolute paths to ensure the scheduler finds them regardless of where it's launched
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTOR = os.path.join(BASE_DIR, "collectors", "reddit_collector.py")
PROCESSOR = os.path.join(BASE_DIR, "processors", "raw_to_clean.py")
LOADER = os.path.join(BASE_DIR, "loaders", "db_loader.py")

# ML Engine bridge (lives in ml_engine/pipelines/)
PROJECT_ROOT = os.path.dirname(BASE_DIR)
ML_RUNNER = os.path.join(PROJECT_ROOT, "ml_engine", "pipelines", "ml_runner.py")

def run_task(script_path, task_name):
    """Helper function to execute a python script and log the result."""
    print(f"--- [START] Starting {task_name} at {datetime.now()} ---")
    try:
        # Runs the script as a separate process utilizing the same python executable (venv)
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"[SUCCESS] {task_name} Finished successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error in {task_name}: {e.stderr}")
        return False

def full_pipeline_job():
    """The master sequence that runs the entire ETL + ML process."""
    print(f"\n[ALERT] SCHEDULED RUN STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Extraction
    if run_task(COLLECTOR, "Data Collection"):
        # 2. Transformation (Only if collection succeeded)
        if run_task(PROCESSOR, "Data Cleaning"):
            # 3. Loading (Only if cleaning succeeded)
            if run_task(LOADER, "Database Loading"):
                # 4. ML Analysis (Only if loading succeeded)
                run_task(ML_RUNNER, "ML Engine Analysis")
            
    print(f"[END] PIPELINE RUN FINISHED at {datetime.now()}\n")

# --- 🕒 SET THE SCHEDULE ---
# Option A: Run every hour for testing
schedule.every(1).hours.do(full_pipeline_job)

# Option B: Run daily at a specific time (e.g., midnight)
# schedule.every().day.at("00:00").do(full_pipeline_job)

# Option C: Run every 10 minutes (Useful for fast-moving trends)
# schedule.every(10).minutes.do(full_pipeline_job)

if __name__ == "__main__":
    print("[INFO] Scheduler is active and waiting for the next run...")
    print("Press Ctrl+C to stop the scheduler.")
    
    # Run once immediately on startup so you don't have to wait for the first hour
    full_pipeline_job()
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute if a job is due
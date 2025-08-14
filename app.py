# app.py
from fastapi import FastAPI
from typing import Optional
import os
import threading
import time
import random
import traceback
import datetime

app = FastAPI()

# Configurable parameters via environment variables
RUN_INTERVAL = int(os.getenv("RUN_INTERVAL_SECONDS", "300"))  # Default: 5 min
RUN_JITTER   = int(os.getenv("RUN_JITTER_SECONDS", "120"))    # Default: ±2 min
ITER_DEFAULT = int(os.getenv("ITERATIONS_PER_RUN", "2"))      # Default: 2 iterations
ENABLE_LOOP  = os.getenv("ENABLE_LOOP", "true").lower() == "true"

def _run_once(n: int):
    """
    Executes a single simulation run with n iterations.
    Lazy import ensures the app starts even if simulator is missing until runtime.
    """
    from simulator import run_test
    run_test(iterations=n)

_stop = False

def loop():
    """
    Background loop that runs the simulation at the specified interval + jitter.
    Logs timestamps for each run to AWS App Runner application logs.
    """
    while not _stop:
        try:
            start_time = datetime.datetime.utcnow().isoformat()
            print(f"[{start_time}] Scheduled run starting...", flush=True)
            
            _run_once(ITER_DEFAULT)
            
            end_time = datetime.datetime.utcnow().isoformat()
            print(f"[{end_time}] Scheduled run completed successfully.", flush=True)

        except Exception as e:
            err_time = datetime.datetime.utcnow().isoformat()
            print(f"[{err_time}] Error in scheduled run: {e}", flush=True)
            traceback.print_exc()

        # Wait before the next run
        sleep_seconds = RUN_INTERVAL + random.randint(0, RUN_JITTER)
        print(f"Sleeping for {sleep_seconds} seconds until next run...", flush=True)
        time.sleep(sleep_seconds)

@app.on_event("startup")
def startup():
    """
    Starts the background scheduler thread on application startup.
    """
    if ENABLE_LOOP:
        print(f"Background loop enabled. Interval={RUN_INTERVAL}s, Jitter={RUN_JITTER}s", flush=True)
        threading.Thread(target=loop, daemon=True).start()
    else:
        print("Background loop disabled by ENABLE_LOOP env var.", flush=True)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/run")
def run_now(iterations: Optional[int] = None):
    """
    Immediately triggers a run with specified iterations (or default if not provided).
    """
    chosen_iters = iterations or ITER_DEFAULT
    print(f"[{datetime.datetime.utcnow().isoformat()}] Manual run triggered with {chosen_iters} iterations.", flush=True)
    _run_once(chosen_iters)
    return {"status": "ok", "iterations": chosen_iters}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

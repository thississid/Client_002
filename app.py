# app.py
from fastapi import FastAPI
from typing import Optional
import os
import sys
import threading
import time
import random
import traceback
import datetime

# --- Helpers ---------------------------------------------------------------
def _int_env(name: str, default: int) -> int:
    val = os.getenv(name)
    if val is None or val.strip() == "":
        return default
    try:
        return int(val)
    except ValueError:
        print(f"Invalid int for {name}='{val}', falling back to {default}", flush=True)
        return default

app = FastAPI()
print(
    f"[BOOT] App module loaded. Python={sys.version.split()[0]} CWD={os.getcwd()}",
    flush=True,
)

# Configurable parameters via environment variables
RUN_INTERVAL = _int_env("RUN_INTERVAL_SECONDS", 300)    # Default: 5 min
RUN_JITTER   = _int_env("RUN_JITTER_SECONDS", 120)      # Default: ±2 min
ITER_DEFAULT = _int_env("ITERATIONS_PER_RUN", 2)        # Default: 2 iterations
ENABLE_LOOP  = os.getenv("ENABLE_LOOP", "true").lower() == "true"
LOOP_START_DELAY = _int_env("LOOP_START_DELAY_SECONDS", 5)  # Grace period before starting loop

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
    """Starts the background scheduler thread on application startup with an optional delay.

    Delay gives the platform (e.g. AWS App Runner) time to mark the service healthy
    before heavy work (CSV + pandas import, etc.) begins.
    """
    try:
        print(
            f"[STARTUP] Settings: ENABLE_LOOP={ENABLE_LOOP} RUN_INTERVAL={RUN_INTERVAL} RUN_JITTER={RUN_JITTER} ITER_DEFAULT={ITER_DEFAULT} START_DELAY={LOOP_START_DELAY}",
            flush=True,
        )
        # Log important file paths & existence
        csv_exists = os.path.isfile(os.getenv("CSV_PATH", "data/Client002.csv"))
        cards_exists = os.path.isfile(os.getenv("CARDS_PATH", "config/cards.json"))
        print(
            f"[STARTUP] CSV_PATH={os.getenv('CSV_PATH','data/Client002.csv')} exists={csv_exists}",
            flush=True,
        )
        print(
            f"[STARTUP] CARDS_PATH={os.getenv('CARDS_PATH','config/cards.json')} exists={cards_exists}",
            flush=True,
        )

        if ENABLE_LOOP:
            print(
                f"[STARTUP] Background loop will start after {LOOP_START_DELAY}s delay.",
                flush=True,
            )

            def _delayed_start():
                if LOOP_START_DELAY > 0:
                    time.sleep(LOOP_START_DELAY)
                loop()

            threading.Thread(target=_delayed_start, daemon=True).start()
        else:
            print("[STARTUP] Background loop disabled by ENABLE_LOOP env var.", flush=True)
    except Exception as e:
        # Never let a startup logging error kill the service
        print(f"[STARTUP][ERROR] Unexpected error during startup logging: {e}", flush=True)
        traceback.print_exc()

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

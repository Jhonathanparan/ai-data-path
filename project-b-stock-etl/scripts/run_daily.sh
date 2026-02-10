#!/bin/bash
set -euo pipefail

# Always run from the project root (launchd does NOT guarantee working directory)
cd "/Users/mac1/Projects/AI-Data-Path/project-b-stock-etl"

# Activate venv
source ".venv/bin/activate"

# Run the daily job and log everything (stdout + stderr)
python -m src.jobs.run_daily >> "logs/run_daily.log" 2>&1
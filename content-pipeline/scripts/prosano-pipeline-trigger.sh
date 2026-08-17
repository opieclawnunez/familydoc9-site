#!/usr/bin/env bash
# Trigger script for the Prosano content pipeline.
# This is the thin cron trigger — it delegates the full content burden to the
# prosano-content-pipeline skill. It does NOT draft articles, prompt FLUX, or
# compose social copy inline. It sets the stage, invokes the skill, and reports.
#
# Schedule: Monday 08:00 Phoenix time (docnunez-weekly-content-creation cron)
set -euo pipefail

REPO="/opt/fleet/workspace/repos/familydoc9-site"
PIPELINE="$REPO/content-pipeline/scripts/pipeline.py"
SKILL_DIR="/home/ubuntu/.hermes/skills/prosano-content-pipeline"
ENVFILE="/home/ubuntu/.hermes/.env"

# --- Pre-flight ---
echo "=== Prosano content pipeline trigger ==="
echo "Repo: $REPO"
echo "Time: $(date -Iseconds)  (Phoenix / MST / UTC-7)"
echo

# Check repo
if [[ ! -d "$REPO" ]]; then
  echo "BLOCKER: repo missing at $REPO"
  exit 1
fi

# Check pipeline.py
if [[ ! -f "$PIPELINE" ]]; then
  echo "BLOCKER: pipeline.py missing at $PIPELINE"
  exit 1
fi

# Check HyperFrames
if ! command -v npx &>/dev/null; then
  echo "BLOCKER: npx not found"
  exit 1
fi

echo "Pre-flight: repo OK, pipeline.py OK, npx OK"
echo

# --- Invoke the skill ---
# The skill is the content engine. This script just sets the topic (if provided)
# and delegates. The skill writes its own manifest.
cd "$REPO"

# Topic selection: environment variable override, or launch-package already present,
# or the skill selects from West Valley context.
if [[ -n "${TOPIC:-}" ]]; then
  echo "Topic override: $TOPIC"
  export PROSANO_TOPIC="$TOPIC"
elif [[ -n "${SLUG:-}" ]]; then
  echo "Launch package slug: $SLUG"
  export PROSANO_LAUNCH_SLUG="$SLUG"
else
  echo "No topic override and no launch slug — skill will select from context."
fi

# Run the skill via Hermes cron invocation.
# The skill is loaded by the cron job's skill list; this script's job is to
# ensure the environment is right and then let the skill do its work.
# In the cron job configuration, this script is the workdir trigger; the actual
# content work is done by the agent running with the prosano-content-pipeline
# skill loaded.

echo
echo "Pipeline trigger complete. Skill invocation is handled by the cron job."
echo "Deliverables expected in: $REPO/content-pipeline/output/weekly-$(date +%Y-%W)/"

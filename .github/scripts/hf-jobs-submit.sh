#!/usr/bin/env bash
#
# Run a Hugging Face Jobs command, reporting "no pre-paid credit" as a skip
# rather than a failure.
#
# HF Jobs is paid and this account's balance is empty, so every `hf jobs` call
# in this repository returns 402. Four workflows dispatch one -- train,
# lighteval, eval, mcp-bench -- and two of those are on a weekly cron, so the
# repository went red every Monday for a reason no commit here can fix. A badge
# that is always red teaches everyone to ignore red badges, which is the same
# argument monitor.yml's header already makes about its own permanent failure.
#
# Only 402 is forgiven, and only when the command actually failed. A rotated
# token, a renamed CLI flag, a missing script, a rejected flavor: all still fail
# the job. Those are repository problems; an empty credit balance is not.
#
# Usage:
#   .github/scripts/hf-jobs-submit.sh hf jobs uv run --flavor a100-large script.py
#
set -uo pipefail

log="${RUNNER_TEMP:-/tmp}/hf-jobs-submit.log"

status=0
"$@" 2>&1 | tee "$log" || status=$?

if [ "$status" -eq 0 ]; then
  exit 0
fi

if grep -qiE '402 Payment Required|credit balance is insufficient' "$log"; then
  echo "::warning::HF Jobs dispatch skipped: this account has no pre-paid Jobs credit (402 Payment Required)."
  {
    echo "## HF Jobs dispatch skipped"
    echo
    echo "\`$*\`"
    echo
    echo "returned **402 Payment Required** -- the Hugging Face account has no pre-paid"
    echo "Jobs credit. Authentication succeeded and the command itself is well-formed, so"
    echo "nothing in this repository is broken. Add credit and re-run to dispatch the job."
  } >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
  exit 0
fi

exit "$status"

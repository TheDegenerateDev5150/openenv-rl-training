---
title: BrowserGym Env
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: apache-2.0
short_description: BrowserGym OpenEnv server for SakThai GRPO RL training
app_port: 7860
---

# BrowserGym Env

> **Not currently deployed.** This directory is the recipe (Dockerfile + this
> Space card), not a running service. The Space it was pushed to,
> `Nanthasit/browsergym-env`, no longer exists — `hf stat` reports it missing and
> both `/` and `/health` on `nanthasit-browsergym-env.hf.space` return 404
> (verified 2026-09-16). Until it is redeployed, `train.py --env browsergym`
> defaults to the upstream
> [`openenv/browsergym_env`](https://huggingface.co/spaces/openenv/browsergym_env).
> After redeploying, pass `--browsergym-url` (or `TRAIN_BROWSERGYM_URL`) to point
> back at your own Space.

BrowserGym environment server for SakThai GRPO reinforcement-learning training.

Supports MiniWoB++ (training) and WebArena (evaluation) benchmarks via the OpenEnv Gymnasium-compatible API.

## Endpoints
- `POST /reset` — Reset environment, returns observation
- `POST /step` — Step with action, returns observation + reward
- `GET /state` — Current episode state
- `GET /health` — Health check

## Usage
```python
from browsergym_env import BrowserGymEnv

# Upstream catalog Space (default in train.py). Swap in your own after redeploying.
env = BrowserGymEnv(base_url="https://openenv-browsergym-env.hf.space")
result = env.reset()
```

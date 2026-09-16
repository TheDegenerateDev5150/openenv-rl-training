"""Make the workspace test suites runnable on a plain CPU checkout.

Both `openenv-custom-training/tests/` and `sakthai-agentic-eval-train/tests/`
were written to run on a box that already had the training stack installed, so
in a clean checkout they failed at collection and no CI job ran them:

    openenv-custom-training/tests/  -> ModuleNotFoundError: No module named 'openenv'
    sakthai-agentic-eval-train/tests/test_eval_bench_peft.py
        -> ModuleNotFoundError: No module named 'huggingface_hub.utils'

Two different causes, handled separately below.

This file stubs ONLY what is genuinely absent. If the real `openenv` is
installed the stub is skipped entirely, so the tests keep their value on a GPU
box and merely become runnable everywhere else.
"""

import sys
import types
from unittest.mock import MagicMock

# --- 1. Import what is really available, before any test module stubs it -----
# test_eval_bench_peft.py mocks a module only `if mod not in sys.modules`.
# `huggingface_hub` ships as a `datasets` dependency, so it is importable — it
# was simply not yet imported when that guard ran, so the guard replaced a real
# package with a bare MagicMock. A MagicMock is not a package, so the module
# under test then failed on `from huggingface_hub.utils import ...`. Importing
# it here first makes the guard do the right thing.
for _name in ("huggingface_hub", "datasets"):
    try:
        __import__(_name)
    except ImportError:
        pass


# --- 2. Stub `openenv` when it is not installed ------------------------------
def _install_openenv_stub():
    """Register an `openenv` package shaped like the surfaces this repo uses.

    `Action`/`Observation` must be real pydantic models: `agent_tools/models.py`
    subclasses them with `Field(...)` defaults, which a MagicMock cannot carry.
    Everything else only needs to be constructible and subclassable.
    """
    try:
        from pydantic import BaseModel
    except ImportError:  # pragma: no cover - pydantic is in the CI invocation
        BaseModel = object

    class Action(BaseModel):
        pass

    class Observation(BaseModel):
        model_config = {"extra": "allow"}

    class State:
        def __init__(self, episode_id=None, step_count=0, **kwargs):
            self.episode_id = episode_id
            self.step_count = step_count
            for key, value in kwargs.items():
                setattr(self, key, value)

    class Environment:
        SUPPORTS_CONCURRENT_SESSIONS = False

    class StepResult:
        """Subscriptable too: client.py annotates `StepResult[Observation]`."""

        def __class_getitem__(cls, item):
            return cls

        def __init__(self, observation=None, reward=None, done=False, metadata=None):
            self.observation = observation
            self.reward = reward
            self.done = done
            self.metadata = metadata

    class EnvClient:
        """Subscriptable so `EnvClient[Action, Observation, State]` resolves."""

        def __class_getitem__(cls, item):
            return cls

        def __init__(self, base_url=None, **kwargs):
            self.base_url = base_url

    def _module(name, **attrs):
        mod = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(mod, key, value)
        sys.modules[name] = mod
        return mod

    _module("openenv")
    core = _module("openenv.core", EnvClient=EnvClient)
    _module("openenv.core.client_types", StepResult=StepResult)
    env_server = _module(
        "openenv.core.env_server", create_app=MagicMock(name="create_app")
    )
    _module(
        "openenv.core.env_server.types",
        Action=Action,
        Observation=Observation,
        State=State,
    )
    _module("openenv.core.env_server.interfaces", Environment=Environment)
    core.env_server = env_server


try:
    import openenv  # noqa: F401
except ImportError:
    _install_openenv_stub()

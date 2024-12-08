def reset_seed():
    """Resets the hashing seed to have deterministic results."""
    import os
    import sys

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

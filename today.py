"""Entry point shim for the ``mochapulse`` package.

Kept at the repository root as ``today.py`` so ``python today.py`` continues to
work unchanged for the CI workflow (``.github/workflows/build.yaml``) and the
README. All logic lives in the :mod:`mochapulse` package; this file only wires
the command line to :func:`mochapulse.build.run`.
"""
from mochapulse.build import run

if __name__ == "__main__":
    run()

"""mochapulse: generate the dark/light SVG profile cards from GitHub data.

The package entry point is :func:`mochapulse.build.run`, invoked by the
repository-root ``today.py`` shim so ``python today.py`` keeps working for CI
and the README.
"""
from .build import run

__all__ = ["run"]

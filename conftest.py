"""
Pytest configuration: ensure the project root is importable so that
`backend.*` and `data.*` packages resolve during tests.
"""
import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

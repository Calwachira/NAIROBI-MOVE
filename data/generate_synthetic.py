"""Regenerate data/trips.csv:  python data/generate_synthetic.py   (works from any folder)"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.synth import generate
print("wrote data/trips.csv", len(generate()), "rows")

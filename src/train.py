"""Train and evaluate:  python src/train.py   (works from any folder)"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.model import train
from src.config import MODEL
b = train(); print("Free-flow minutes:", {k: round(v) for k, v in b["free"].items()}); print("Saved", MODEL)

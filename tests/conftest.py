"""Configuration commune aux tests : ajoute la racine du dépôt au PYTHONPATH."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

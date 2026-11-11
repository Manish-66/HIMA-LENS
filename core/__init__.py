"""
HIMA-LENS Core Geotechnical, AI Vision & Photogrammetry Engines
"""
from pathlib import Path
import sys

CORE_DIR = Path(__file__).resolve().parent
ROOT_DIR = CORE_DIR.parent

if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

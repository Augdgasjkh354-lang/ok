#!/usr/bin/env python3
"""Recommended rebuild for the self-contained v7.5 source release."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'build_v75_fast.py')],cwd=root,check=True)

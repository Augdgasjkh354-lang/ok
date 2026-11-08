#!/usr/bin/env python3
"""Reapply all v7.x Chinese localization, including the v7.5 cooldown reply."""
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent.parent
subprocess.run([sys.executable, str(root/'scripts/finalize_fb_v74.py')], cwd=root, check=True)
p = root/'game-data/conversation.txt'
data = p.read_bytes()
needle = b'I_have_already_shared_my_latest_whispers._Ask_me_again_in_{reg59}_days.'
assert data.count(needle) == 1, (needle, data.count(needle))
data = data.replace(needle, '我最近已经告诉过你这些风声。请再过{reg59}天来打听。'.encode('utf-8'))
p.write_bytes(data)
print('Localized v7.5 gossip cooldown response.')

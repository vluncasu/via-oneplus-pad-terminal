#!/usr/bin/env python3
"""Verify the exact bundled build-time hand model; no runtime network download."""
from pathlib import Path
import hashlib
p=Path(__file__).resolve().parents[1]/'android/core-vision/src/main/assets/hand_landmarker.task'
expected='fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1'
assert p.is_file(), 'Hand model is missing; follow the official asset URL in the asset README.'
assert hashlib.sha256(p.read_bytes()).hexdigest()==expected, 'Hand model checksum mismatch'
print('Bundled hand model checksum verified.')

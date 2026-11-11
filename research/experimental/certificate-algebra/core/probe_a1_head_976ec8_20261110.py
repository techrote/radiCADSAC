"""Replay a genuine 976ec8 A1 receipt through the B1 source-codec refusal gate.

Run from the B1 research directory:
  python3 probe_a1_head_976ec8_20261110.py --a1-dir /path/to/A1/isolator
Two detached exact-head checkouts are required; no physical-source custody is claimed.
"""
import argparse
import json
from pathlib import Path
import probe_current_a1_receipt_20261110 as original

# Exact source identities published on A1 #470, not implied by old adapter tags.
original.A1_HEAD = "976ec8c093a17bbe117b7ddd14dc4f391c7ea25c"
original.A1_BLOBS = {
    "algebraic_zero.py": "5a8e52898725aa10b427de4e5736cb1cf5578d68",
    "receipt_integrity.py": "77f0ba7700002b7a376dfcc2c29b820ea4def485",
}

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--a1-dir", type=Path, required=True)
    print(json.dumps(original.run(cli.parse_args().a1_dir.resolve()), sort_keys=True, indent=2))

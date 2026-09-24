"""Top-level SDK example: python examples/receive_minimal.py.

Install mx-eye first or run from an IDE with the project folder on sys.path.
"""
import time
from app import Client

TRACKER_IP = '127.0.0.1'

with Client(TRACKER_IP) as eye:
    eye.start()
    try:
        while True:
            sample = eye.latest(max_age_ms=50)
            if sample is not None:
                # Pixel signal: pupil minus CR, or pupil coordinates in pupil-only mode.
                print(f'x={sample.x:7.2f}  y={sample.y:7.2f}  age≈{sample.age_ms:5.2f} ms')
            time.sleep(0.02)
    except KeyboardInterrupt:
        eye.stop()

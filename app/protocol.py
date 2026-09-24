"""Version 1 mx_eye wire format; intentionally distinct from transport test v4."""
import struct

MAGIC = b'MXEY'
VERSION = 1
VALID = 1
PUPIL = 2
CR = 4
PUPIL_ONLY = 8
SIMULATION = 16
ROI_RELATIVE = 32
# magic/version/flags/reserved; session, sequence, frame, acquisition,
# tracking-start, tracking-end, send (all uint64); media time (signed ns);
# x,y,pupil-x,pupil-y,CR-x,CR-y,pupil-area,template-NCC (float32).
PACKET = struct.Struct('<4sBBH7Qq8f')

def decode(data):
    if len(data) != PACKET.size:
        raise ValueError('Invalid mx_eye packet size')
    p = PACKET.unpack(data)
    if p[0] != MAGIC or p[1] != VERSION:
        raise ValueError('Unsupported mx_eye protocol')
    return p

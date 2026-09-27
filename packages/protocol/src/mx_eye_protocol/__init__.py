"""Shared wire formats between the mx-eye tracker and the mx-eye SDK.

This package holds the versioned wire contract only: the binary packet layout
and the control-plane messages. It depends on the standard library alone and
must not import Qt, OpenCV, or the tracker.
"""
from .packets import (MAGIC, VERSION, PACKET, VALID, PUPIL, CR, PUPIL_ONLY,
                      SIMULATION, ROI_RELATIVE, Packet, decode, encode)
from .control import (PROTOCOL_VERSION, CMD_STATUS, CMD_START, CMD_STOP, CMD_SYNC,
                      CONTROL_COMMANDS, SYNC_COMMANDS, Request, Reply, StatusSnapshot)

__version__ = '0.1.0'
__all__ = ['MAGIC', 'VERSION', 'PACKET', 'VALID', 'PUPIL', 'CR', 'PUPIL_ONLY',
           'SIMULATION', 'ROI_RELATIVE', 'Packet', 'decode', 'encode',
           'PROTOCOL_VERSION', 'CMD_STATUS', 'CMD_START', 'CMD_STOP', 'CMD_SYNC',
           'CONTROL_COMMANDS', 'SYNC_COMMANDS', 'Request', 'Reply', 'StatusSnapshot']

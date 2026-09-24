"""Versioned, portable settings. All image coordinates use source pixels."""
import copy
import json
import math
from pathlib import Path

TRACKING_DEFAULTS = dict(
    pupil_thr=48, pupil_min=30, pupil_max=3000,
    cr_thr=181, cr_min=2, cr_max=120, pupil_gate=7, cr_gate=2,
    max_pair_dist=10, max_pair_vec_change=4, reacquire_after_frames=4,
    template_radius=35, template_search_size=520, template_min_corr=0.60,
    tracking_mode='Pupil + CR', pupil_coordinates='absolute', template_tracking=False)

DEFAULTS = dict(
    format='mx-eye', version=1,
    source=dict(mode='camera', camera=0, path='', width=640, height=480,
                fps=120.0, backend='auto', fourcc='MJPG', speed=1.0),
    tracking=dict(TRACKING_DEFAULTS, roi=[0, 0, 320, 240]),
    network=dict(bind='127.0.0.1', data_port=5556, control_port=5557,
                 sync_port=5558, transport='tcp', udp_host='127.0.0.1'),
    recording=dict(directory='recordings', buffer_mb=128, codec='MJPG',
                   record_simulation=False),
    display=dict(hz=25, masks=True, crosshairs=True), template=None)

def defaults():
    return copy.deepcopy(DEFAULTS)

def validate(config):
    c = copy.deepcopy(config)
    if c.get('format') != 'mx-eye' or c.get('version') != 1:
        raise ValueError('Unsupported mx_eye configuration version.')
    s, n, t, r = (c[k] for k in ['source', 'network', 'tracking', 'recording'])
    if s['mode'] not in ('camera', 'video', 'simulation'):
        raise ValueError('Source must be camera, video or simulation.')
    if n['transport'] not in ('tcp', 'udp'):
        raise ValueError('Transport must be tcp or udp.')
    ports = [int(n[k]) for k in ('data_port', 'control_port', 'sync_port')]
    if len(set(ports)) != 3 or any(not 1024 <= p <= 65535 for p in ports):
        raise ValueError('Use three distinct ports between 1024 and 65535.')
    for k in ('width', 'height'):
        if not 32 <= s[k] <= 16384:
            raise ValueError('Source dimensions must be 32–16384 pixels.')
    if not 1 <= s['fps'] <= 1000 or not 0.05 <= s['speed'] <= 8:
        raise ValueError('Invalid frame rate or playback speed.')
    if s['backend'] not in ('auto', 'dshow', 'msmf', 'v4l2'):
        raise ValueError('Unsupported camera backend.')
    if len(s['fourcc']) != 4 or r['codec'] not in ('MJPG', 'FFV1'):
        raise ValueError('Camera FOURCC needs four characters; recording codec is MJPG or FFV1.')
    if not 8 <= r['buffer_mb'] <= 2048:
        raise ValueError('Recording buffer must be 8–2048 MiB.')
    for k, value in t.items():
        if k in TRACKING_DEFAULTS and isinstance(TRACKING_DEFAULTS[k], (int, float)):
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'Invalid tracking parameter: {k}')
    for k in ('pupil_thr', 'cr_thr'):
        if not 0 <= t[k] <= 255:
            raise ValueError('Thresholds must be between 0 and 255.')
    for prefix in ('pupil', 'cr'):
        if not 0 <= t[prefix+'_min'] <= t[prefix+'_max']:
            raise ValueError('Minimum blob area must not exceed maximum.')
    for k in ('pupil_gate', 'cr_gate', 'max_pair_dist', 'max_pair_vec_change', 'reacquire_after_frames', 'template_radius', 'template_search_size'):
        if t[k] <= 0:
            raise ValueError(f'{k} must be positive.')
    if not 0 <= t['template_min_corr'] <= 1:
        raise ValueError('Template correlation must be 0–1.')
    if t['tracking_mode'] not in ('Pupil + CR', 'Pupil only'):
        raise ValueError('Invalid tracking mode.')
    if t.get('pupil_coordinates','absolute') not in ('absolute','relative'):
        raise ValueError('Pupil coordinates must be absolute or relative.')
    if len(t['roi']) != 4 or not all(math.isfinite(x) for x in t['roi']) or min(t['roi'][2:]) < 1:
        raise ValueError('ROI must contain x, y, width, height.')
    return c

def load(path):
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    c = defaults()
    if raw.get('format') == 'mxbi-eye-tracker-config':
        # Import existing v13 JSON; its template image was stored separately.
        c['tracking'].update({k:v for k,v in raw.get('settings', {}).items() if k in TRACKING_DEFAULTS})
        c['tracking']['roi'] = raw['roi']
        c['tracking']['tracking_mode'] = raw.get('tracking_mode', 'Pupil + CR')
        old_display=raw.get('display',{})
        for old,new in [('show_pupil_mask','pupil_mask'),('show_cr_mask','cr_mask'),('show_crosshairs','crosshairs')]:
            if old in old_display: c['display'][new]=old_display[old]
        c['tracking']['template_tracking']=old_display.get('template_tracking',False)
    else:
        for k, v in raw.items():
            if isinstance(v, dict) and isinstance(c.get(k), dict):
                c[k].update(v)
            else:
                c[k] = v
    return validate(c)

def save(path, config):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(validate(config), indent=2, allow_nan=False), encoding='utf-8')
    temp.replace(path)

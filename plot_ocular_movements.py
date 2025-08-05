import sys
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "<remodnav_out_file>")
    sys.exit(1)

input_file = sys.argv[1]

colors = {
    'SACC': 'orange', 'ISAC': 'red',
    'FIXA': 'green', 'PURS': 'blue',
    'LPSO': 'black', 'HPSO': 'gray',
    'ILPS': 'black', 'IHPS': 'yellow'
}

with open(input_file) as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
idx = {key: header.index(key) for key in ['label', 'start_x', 'start_y', 'end_x', 'end_y', 'onset', 'duration']}

segments = []
saccades = []

for line in lines[1:]:
    data = line.strip().split('\t')
    event = data[idx['label']]
    if event not in colors:
        continue
    seg = {
        'event': event,
        'x1': float(data[idx['start_x']]),
        'y1': float(data[idx['start_y']]),
        'x2': float(data[idx['end_x']]),
        'y2': float(data[idx['end_y']]),
        'onset': float(data[idx['onset']]),
        'duration': float(data[idx['duration']]),
        'color': colors[event]
    }
    segments.append(seg)
    if event == 'SACC':
        saccades.append(((seg['x1'], seg['y1']), (seg['x2'], seg['y2']), seg['onset']))

# --- PLOT 3D MOVEMENTS ---
fig3d = plt.figure()
ax3d = fig3d.add_subplot(111, projection='3d')
used_labels = set()

for seg in segments:
    label = seg['event'] if seg['event'] not in used_labels else None
    ax3d.plot([seg['x1'], seg['x2']],
              [seg['onset'], seg['onset'] + seg['duration']],
              [seg['y1'], seg['y2']],
              color=seg['color'], label=label)
    used_labels.add(seg['event'])

ax3d.set_xlabel('X')
ax3d.set_ylabel('Time')
ax3d.set_zlabel('Y')
ax3d.set_title('Dominant Eye Direction (3D)')
ax3d.view_init(elev=20., azim=-35)
ax3d.legend()
plt.show()

# --- PLOT 2D MOVEMENTS ---
fig2d, (ax_x, ax_y) = plt.subplots(2, 1, figsize=(10, 6))
used_labels.clear()

for seg in segments:
    x1_deg = seg['x1'] * 0.068055
    x2_deg = seg['x2'] * 0.068055
    y1_deg = seg['y1'] * 0.068055
    y2_deg = seg['y2'] * 0.068055
    t1 = seg['onset']
    t2 = seg['onset'] + seg['duration']
    label = seg['event'] if seg['event'] not in used_labels else None
    ax_x.plot([t1, t2], [x1_deg, x2_deg], color=seg['color'], label=label)
    ax_y.plot([t1, t2], [y1_deg, y2_deg], color=seg['color'], label=label)
    used_labels.add(seg['event'])

ax_x.set_ylabel("Direction X (deg)")
ax_y.set_ylabel("Direction Y (deg)")
ax_y.set_xlabel("Time (s)")
fig2d.suptitle("Dominant Gaze Direction (2D)")
ax_x.legend()
plt.tight_layout()
plt.show()


# --- PLOT SACCADE DIRECTION POLAR ---
fig_polar = plt.figure()
ax_polar = fig_polar.add_subplot(111, polar=True)

for (x1, y1), (x2, y2), _ in saccades:
    dx = x2 - x1
    dy = y2 - y1
    angle = np.arctan2(dy, dx)
    magnitude = np.hypot(dx, dy)
    ax_polar.plot([angle], [magnitude], 'o', color='orange', alpha=0.5)

ax_polar.set_title("Saccade Directions (Polar)")
plt.show()

# --- PLOT SACCADE DIRECTION 3D ---
fig_sacc3d = plt.figure()
ax_sacc3d = fig_sacc3d.add_subplot(111, projection='3d')

for (x1, y1), (x2, y2), onset in saccades:
    ax_sacc3d.quiver(x1, onset, y1, x2 - x1, 0, y2 - y1, color='orange', alpha=0.6)

ax_sacc3d.set_xlabel('X')
ax_sacc3d.set_ylabel('Time')
ax_sacc3d.set_zlabel('Y')
ax_sacc3d.set_title("Saccade Directions (3D)")
ax_sacc3d.view_init(elev=20., azim=-35)
plt.show()

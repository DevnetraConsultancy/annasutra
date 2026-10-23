"""
Test script for Producer Harvest Lot SVG Chart generation.
"""

def generate_svg_donut(slices, total_num, unit_label="Kg"):
    cx, cy, r_outer, r_inner = 130, 130, 105, 68
    import math
    
    total = sum(s['value'] for s in slices) or 1
    paths = []
    current_angle = -90.0  # Start at top
    
    for s in slices:
        val = s['value']
        if val <= 0:
            continue
        slice_angle = (val / total) * 360.0
        # If full circle
        if slice_angle >= 359.9:
            slice_angle = 359.9
            
        start_rad = math.radians(current_angle)
        end_rad = math.radians(current_angle + slice_angle)
        
        x1_out = cx + r_outer * math.cos(start_rad)
        y1_out = cy + r_outer * math.sin(start_rad)
        x2_out = cx + r_outer * math.cos(end_rad)
        y2_out = cy + r_outer * math.sin(end_rad)
        
        x1_in = cx + r_inner * math.cos(end_rad)
        y1_in = cy + r_inner * math.sin(end_rad)
        x2_in = cx + r_inner * math.cos(start_rad)
        y2_in = cy + r_inner * math.sin(start_rad)
        
        large_arc = 1 if slice_angle > 180 else 0
        
        d = f"M {x1_out:.1f} {y1_out:.1f} A {r_outer} {r_outer} 0 {large_arc} 1 {x2_out:.1f} {y2_out:.1f} L {x1_in:.1f} {y1_in:.1f} A {r_inner} {r_inner} 0 {large_arc} 0 {x2_in:.1f} {y2_in:.1f} Z"
        pct = (val / total) * 100.0
        tooltip = f"{s['label']}: {val:,.1f} {unit_label} ({pct:.1f}%)"
        paths.append(f'<path d="{d}" fill="{s["color"]}" stroke="#ffffff" stroke-width="2.5"><title>{tooltip}</title></path>')
        current_angle += slice_angle
        
    svg = f'''<svg viewBox="0 0 260 260" width="100%" height="260" style="overflow: visible; display: block; margin: 0 auto;">
      {' '.join(paths)}
      <circle cx="{cx}" cy="{cy}" r="{r_inner - 2}" fill="#ffffff"/>
      <text x="{cx}" y="{cy - 6}" font-size="20" font-weight="900" fill="#0b3d2e" text-anchor="middle">{total_num:,.0f}</text>
      <text x="{cx}" y="{cy + 14}" font-size="11" font-weight="700" fill="#64748b" text-anchor="middle">{unit_label}</text>
    </svg>'''
    return svg

test_slices = [
    {'label': 'Tomato', 'value': 2400, 'color': '#ef4444'},
    {'label': 'Potato', 'value': 4800, 'color': '#f59e0b'},
    {'label': 'Onion', 'value': 1600, 'color': '#8b5cf6'},
    {'label': 'Cauliflower', 'value': 850, 'color': '#10b981'}
]

res = generate_svg_donut(test_slices, 9650, 'Kg')
print("Generated Donut SVG length:", len(res))
assert '<path' in res
assert '<circle' in res
print("Donut test passed.")


def generate_svg_timeline(data_points):
    w, h = 500, 220
    pad_l, pad_r, pad_t, pad_b = 45, 20, 25, 35
    pw = w - pad_l - pad_r
    ph = h - pad_t - pad_b
    
    if not data_points:
        return f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}"><text x="{w/2}" y="{h/2}" fill="#94a3b8" text-anchor="middle">No chronological harvest events recorded</text></svg>'
        
    max_val = max(p['qty'] for p in data_points) or 1
    # round up max_val nicely
    max_y = max_val * 1.2
    
    n = len(data_points)
    coords = []
    for i, p in enumerate(data_points):
        x = pad_l + (i / max(1, n - 1)) * pw if n > 1 else pad_l + pw / 2
        y = pad_t + ph - (p['qty'] / max_y) * ph
        coords.append((x, y, p))
        
    # Build path
    line_parts = [f"M {coords[0][0]:.1f} {coords[0][1]:.1f}"]
    for i in range(1, len(coords)):
        x_prev, y_prev, _ = coords[i-1]
        x_curr, y_curr, _ = coords[i]
        cx1 = x_prev + (x_curr - x_prev) / 2
        cx2 = cx1
        line_parts.append(f"C {cx1:.1f} {y_prev:.1f}, {cx2:.1f} {y_curr:.1f}, {x_curr:.1f} {y_curr:.1f}")
        
    line_d = " ".join(line_parts)
    area_d = f"{line_d} L {coords[-1][0]:.1f} {pad_t + ph} L {coords[0][0]:.1f} {pad_t + ph} Z"
    
    # Grid lines
    grid_svg = []
    for step in range(4):
        gy = pad_t + (step / 3) * ph
        gval = max_y * (1 - step / 3)
        grid_svg.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w - pad_r}" y2="{gy:.1f}" stroke="#f1f5f9" stroke-width="1" stroke-dasharray="3,3"/>')
        grid_svg.append(f'<text x="{pad_l - 8}" y="{gy + 3:.1f}" font-size="9" fill="#94a3b8" text-anchor="end">{gval:,.0f}</text>')
        
    # Markers
    marker_svg = []
    for x, y, p in coords:
        tip = f"{p['label']}: {p['qty']:,.1f} Kg"
        marker_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#ffffff" stroke="#047857" stroke-width="2.5"><title>{tip}</title></circle>')
        marker_svg.append(f'<text x="{x:.1f}" y="{pad_t + ph + 16}" font-size="10" font-weight="600" fill="#64748b" text-anchor="middle">{p["label"]}</text>')
        
    svg = f'''<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" style="overflow: visible;">
      <defs>
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#047857" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="#10b981" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      {' '.join(grid_svg)}
      <path d="{area_d}" fill="url(#areaGrad)"/>
      <path d="{line_d}" fill="none" stroke="#047857" stroke-width="3" stroke-linecap="round"/>
      {' '.join(marker_svg)}
    </svg>'''
    return svg

test_pts = [
    {'label': '10 Oct', 'qty': 450},
    {'label': '14 Oct', 'qty': 1200},
    {'label': '18 Oct', 'qty': 850},
    {'label': '21 Oct', 'qty': 2100},
    {'label': '23 Oct', 'qty': 1600}
]
res2 = generate_svg_timeline(test_pts)
print("Timeline SVG length:", len(res2))
assert '<path d="M' in res2
assert 'linearGradient' in res2
print("Timeline test passed.")

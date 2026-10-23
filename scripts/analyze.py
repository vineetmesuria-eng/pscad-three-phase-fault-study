"""Reproduce the PSCAD study metrics and figures from the supplied exports.

Run from any directory: python scripts/analyze.py
Calculations and SVG figures use only the Python standard library.
"""
import csv
import hashlib
import json
import math
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'


def read_export(name, columns):
    path = ROOT / 'data' / name
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream)
        headers = [s.strip() for s in next(reader)]
        rows = [[float(x) for x in row] for row in reader if row]
    if len(headers) != columns or len(rows) != 4001:
        raise ValueError(f'{name}: unexpected column or sample count')
    if any(len(r) != columns or not all(math.isfinite(x) for x in r) for r in rows):
        raise ValueError(f'{name}: invalid numeric data')
    if rows[0][0] != 0 or rows[-1][0] != 1:
        raise ValueError(f'{name}: expected a complete 0-1 s export')
    if any(abs(b[0] - a[0] - 0.00025) > 1e-10 for a, b in zip(rows, rows[1:])):
        raise ValueError(f'{name}: expected uniformly spaced 250 us samples')
    return rows


def rms(values):
    return math.sqrt(sum(x*x for x in values)/len(values))


def draw_chart(path, title, panels, xmin, xmax):
    """Write static vector plots directly from all exported samples in range."""
    colors=['#2563eb','#d97706','#059669']
    height=120+len(panels)*270
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<g font-family="Arial, sans-serif" fill="#0f172a">',
         f'<text x="90" y="32" font-size="21" font-weight="bold">{escape(title)}</text>',
         '<text x="90" y="57" font-size="13">Dashed grey: fault starts at 0.50 s. Dotted purple: breaker opening command.</text>']
    for n,panel in enumerate(panels):
        top=105+n*270
        x0,y0,w,h=90,top,940,185
        ymin,ymax=panel['limits']
        def X(t): return x0+(t-xmin)/(xmax-xmin)*w
        def Y(v): return y0+h-(v-ymin)/(ymax-ymin)*h
        svg.append(f'<text x="90" y="{top-16}" font-size="16" font-weight="bold">{escape(panel["title"])}</text>')
        for k in range(6):
            t=xmin+(xmax-xmin)*k/5
            xx=X(t)
            svg.append(f'<path d="M{xx:.2f},{y0}V{y0+h}" stroke="#e2e8f0"/>')
            svg.append(f'<text x="{xx:.2f}" y="{y0+h+22}" text-anchor="middle" font-size="12">{t:.2f}</text>')
        for value in panel['ticks']:
            yy=Y(value)
            svg.append(f'<path d="M{x0},{yy:.2f}H{x0+w}" stroke="#e2e8f0"/>')
            svg.append(f'<text x="{x0-12}" y="{yy+4:.2f}" text-anchor="end" font-size="12">{value:g}</text>')
        svg.append(f'<path d="M{x0},{y0}V{y0+h}H{x0+w}" fill="none" stroke="#64748b"/>')
        svg.append(f'<text x="560" y="{y0+h+45}" text-anchor="middle" font-size="13">Time (s)</text>')
        svg.append(f'<text transform="translate(24,{y0+h/2}) rotate(-90)" text-anchor="middle" font-size="13">{escape(panel["unit"])}</text>')
        svg.append(f'<defs><clipPath id="plot{n}"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath></defs>')
        svg.append(f'<g clip-path="url(#plot{n})">')
        for j,col in enumerate(panel['columns']):
            points=' '.join(f'{X(r[0]):.2f},{Y(r[col]):.2f}' for r in panel['rows'] if xmin<=r[0]<=xmax)
            svg.append(f'<polyline points="{points}" fill="none" stroke="{colors[j]}" stroke-width="1.35"/>')
        for t,color,dash in [(.5,'#475569','6 4'),(panel['command'],'#9333ea','2 4')]:
            svg.append(f'<path d="M{X(t):.2f},{y0}V{y0+h}" stroke="{color}" stroke-width="1.5" stroke-dasharray="{dash}"/>')
        svg.append('</g>')
        if len(panel['columns'])==3:
            for j,color in enumerate(colors):
                svg.append(f'<text x="{760+j*90}" y="{top-16}" font-size="12" fill="{color}">Phase {j+1}</text>')
    svg+=['</g>','</svg>']
    path.write_text('\n'.join(svg),encoding='utf-8')


def measure(name, delay_ms, step_us):
    rows = read_export(name, 4)
    command = 0.5 + delay_ms / 1000
    phases = []
    for col in range(1, 4):
        last = max(k for k, row in enumerate(rows) if row[0] >= 0.5 and abs(row[col]) > 0.001)
        if last == len(rows)-1:
            raise ValueError(f'{name}: phase {col} has not interrupted within the recording')
        energy = sum((b[0]-a[0])*(a[col]**2+b[col]**2)/2
                     for a,b in zip(rows,rows[1:]) if a[0]>=0.5 and b[0]<=0.7)
        phases.append({
            'export_phase': col,
            'normal_rms_A_040_050': 1000*rms([r[col] for r in rows if 0.4<=r[0]<0.5]),
            'fault_rms_kA': rms([r[col] for r in rows if command-0.03<=r[0]<command-0.01]),
            'fault_peak_kA': max(abs(r[col]) for r in rows if r[0]>=0.5),
            'last_sample_above_1A_s': rows[last][0],
            'next_sample_s': rows[last+1][0],
            'I2t_kA2s_050_070': energy,
        })
    return {
        'file':name, 'delay_ms':delay_ms, 'solution_step_us':step_us,
        'fault_rms_window_s':[command-0.03,command-0.01],
        'peak_kA':max(p['fault_peak_kA'] for p in phases),
        'mean_phase_I2t_kA2s':sum(p['I2t_kA2s_050_070'] for p in phases)/3,
        'final_last_above_1A_s':max(p['last_sample_above_1A_s'] for p in phases),
        'final_next_sample_s':max(p['next_sample_s'] for p in phases),
        'phases':phases,
    }, rows


def main():
    RESULTS.mkdir(exist_ok=True)
    cases=[]
    currents={}
    voltages={}
    for delay in (50,100,150):
        case,rows=measure(f'ABCG_{delay}ms_current.csv',delay,50)
        cases.append(case)
        currents[delay]=rows
        voltages[delay]=read_export(f'ABCG_{delay}ms_voltage.csv',2)
    fine,fine_rows=measure('ABCG_100ms_dt25us_current.csv',100,25)
    baseline=cases[1]
    sensitivity={key:100*(fine[key]/baseline[key]-1)
                 for key in ('peak_kA','mean_phase_I2t_kA2s')}
    # Fault shunt is in parallel with the 100-ohm phase load.
    r_parallel=1/(1/0.01+1/100)
    phase_voltage=11000/math.sqrt(3)
    x=2*math.pi*50*0.003
    theory={
        'nominal_source_phase_rms_V':phase_voltage,
        'feeder_reactance_ohm':x,
        'normal_rms_A':phase_voltage/abs(complex(0.2+0.001+0.5+100,x)),
        'fault_rms_kA':phase_voltage/abs(complex(0.2+0.001+0.5+r_parallel,x))/1000,
    }
    report={'cases':cases,'fine_step_case':fine,'fine_step_percent_change':sensitivity,'theory':theory,
            'I2t_reduction_150_to_50_percent':100*(1-cases[0]['mean_phase_I2t_kA2s']/cases[2]['mean_phase_I2t_kA2s'])}
    (RESULTS/'metrics.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    lines=['# Measured results','',
           'Command delay is measured from fault inception at 0.50 s. These are educational model results.','',
           '| Command delay | Command time | Largest sampled peak | Last sample above 1 A | Mean phase I²t |',
           '|---|---|---|---|---|']
    for c in cases:
        lines.append(f"| {c['delay_ms']} ms | {0.5+c['delay_ms']/1000:.2f} s | {c['peak_kA']:.3f} kA | {c['final_last_above_1A_s']:.5f} s | {c['mean_phase_I2t_kA2s']:.3f} kA²s |")
    lines+=['','I²t: trapezoidal integration of instantaneous phase current squared over 0.50–0.70 s, followed by averaging the three phase integrals. This is current exposure, not measured temperature or a protection rating.',
            '','The next sample (250 µs later) is below 1 A. This threshold-based interval is an observation from the exports, not an exact contact-opening time.',
            '',f"Reducing command delay from 150 to 50 ms reduces mean phase I²t by {report['I2t_reduction_150_to_50_percent']:.1f}%.",
            '','## Time-step sensitivity','',
            f"For the 100 ms case, reducing the calculation step from 50 to 25 µs changes largest sampled peak by {sensitivity['peak_kA']:.4f}% and mean phase I²t by {sensitivity['mean_phase_I2t_kA2s']:.4f}%. The 250 µs exported sampling remains unchanged.",
            '','See [methodology](../docs/methodology.md) for calculation windows, assumptions and limitations.','']
    (RESULTS/'comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    manifest={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
              for folder in ('data','model') for p in sorted((ROOT/folder).glob('*')) if p.is_file()}
    (RESULTS/'source_sha256.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    draw_chart(RESULTS/'baseline.svg','100 ms baseline: current interruption and load-voltage collapse',[
        {'title':'Feeder phase currents','rows':currents[100],'columns':[1,2,3],'limits':(-10,10),'ticks':[-10,-5,0,5,10],'command':.6,'unit':'Current (kA)'},
        {'title':'Load-bus RMS voltage','rows':voltages[100],'columns':[1],'limits':(0,1.1),'ticks':[0,.25,.5,.75,1],'command':.6,'unit':'Voltage (pu)'}],0,1)
    draw_chart(RESULTS/'delay_comparison.svg','Earlier opening reduces fault-current duration',[
        {'title':f'{delay} ms opening-command delay','rows':currents[delay],'columns':[1,2,3],'limits':(-10,10),'ticks':[-10,-5,0,5,10],'command':.5+delay/1000,'unit':'Current (kA)'}
        for delay in (50,100,150)],.48,.69)
    print(json.dumps({'mean_I2t':[c['mean_phase_I2t_kA2s'] for c in cases],'sensitivity_percent':sensitivity,'theory':theory},indent=2))


if __name__=='__main__':
    main()

"""Resolve installed Bambu profiles for a geometry-only PETG slicing trial."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
profiles=Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
index={}
for p in profiles.rglob('*.json'):
    try:
        d=json.loads(p.read_text())
        if 'name' in d: index[d['name']]=d
    except Exception: pass
def resolve(name):
    d=index[name]; out={}
    if d.get('inherits'): out.update(resolve(d['inherits']))
    for n in d.get('include',[]): out.update(resolve(n))
    out.update(d); out.pop('inherits',None); out.pop('include',None)
    return out
target=ROOT/'validation/slicer'; target.mkdir(exist_ok=True)
m=resolve('Bambu Lab P1S 0.4 nozzle')
p=resolve('0.12mm Fine @BBL P1P')
f=resolve('Generic PETG @BBL P1P')
p.update(name='R01 Geometry Trial 0.20 PETG',layer_height='0.2',initial_layer_print_height='0.2',enable_support='1',support_type='normal(auto)',support_on_build_plate_only='0',brim_type='outer_only',brim_width='5',wall_loops='6',sparse_infill_density='20%',compatible_printers=['Bambu Lab P1S 0.4 nozzle'],outer_wall_speed=['35'],outer_wall_acceleration=['1000'])
f['compatible_printers']=['Bambu Lab P1S 0.4 nozzle']
for key,d in [('machine',m),('process',p),('filament',f)]: (target/(key+'.json')).write_text(json.dumps(d,indent=2))
print(target)

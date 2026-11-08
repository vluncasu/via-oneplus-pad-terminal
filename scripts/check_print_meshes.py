#!/usr/bin/env python3
"""Audit the published STL inventory without modifying geometry. pip install trimesh numpy."""
import json, hashlib
from pathlib import Path
import trimesh
ROOT=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    for entry in json.loads((ROOT/'hardware/parts.json').read_text()):
        path=ROOT/entry['file'];mesh=trimesh.load_mesh(path,process=True)
        ext=mesh.extents.tolist()
        rows.append(dict(id=entry['id'],file=entry['file'],quantity=entry['quantity'],optional=entry['optional'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),triangles=len(mesh.faces),watertight=bool(mesh.is_watertight),winding_consistent=bool(mesh.is_winding_consistent),bounds_mm=[round(float(v),4) for v in ext],nominal_256mm_box_fit=bool(all(0<v<=256 for v in ext)),volume_mm3=round(float(mesh.volume),3)))
    report=dict(scope='Geometric checks only. Bounding-box fit excludes brim, supports, purge and slicer exclusion zones. No physical print or material-strength validation.',parts=rows)
    output=ROOT/'hardware/validation/print-mesh-audit.json';output.write_text(json.dumps(report,indent=2)+'\n')
    failures=[x for x in rows if not x['watertight'] or not x['winding_consistent'] or not x['nominal_256mm_box_fit']]
    print(json.dumps(dict(files=len(rows),required_quantity=sum(x['quantity'] for x in rows if not x['optional']),failures=failures),indent=2))
    return 1 if failures else 0
if __name__=='__main__':raise SystemExit(main())

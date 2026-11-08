"""Build the English part catalog from inventory and scoped mesh-audit data."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
parts=json.loads((r/'hardware/parts.json').read_text())
audit={p['id']:p for p in json.loads((r/'hardware/validation/print-mesh-audit.json').read_text())['parts']}
lines=['# Printable Part Catalog','', 'Generated from the release inventory. Bounds are X × Y × Z in the **supplied STL print orientation**, not assembly dimensions. Numbers are rounded to two decimals. Quantity is the total copies of the one file; reference objects R01–R05 are excluded.','']
lines += ['| Required color group | Unique files | Printed pieces |','|---|---:|---:|']
for material in ['white PETG','black PETG','natural PETG']:
 group=[p for p in parts if not p['optional'] and p['material']==material]
 lines.append(f"| {material} | {len(group)} | {sum(p['quantity'] for p in group)} |")
lines += ['']
for title,optional in [('Required components',False),('Optional low-material probes',True)]:
 lines += ['## '+title,'','| IDs | Part / file | Copies | Filament | Supplied STL bounds (mm) |','|---|---|---:|---|---|']
 for p in parts:
  if p['optional']!=optional:continue
  a=audit[p['id']];dims=' × '.join(f"{v:.2f}" for v in a['bounds_mm'])
  lines.append(f"| {', '.join(p['part_ids'])} | [{p['name']}](../{p['file']}) | {p['quantity']} | {p['material']} | {dims} |")
 lines += ['']
lines += ['## Alternatives and reference envelopes','','O05 0.40 mm is an optional replacement for the 0.20 mm default, not an extra required piece. R01 tablet, R02 supply, R03 USB plug and R04/R05 LED volumes are inspection references, not printable hardware.','', 'White PETG: structural pieces and printed fasteners. Black PETG: P01, O01, O03 and O06. Natural PETG: O05. The present rigid feet are not TPU pads.','', '## Reading the file families','','- B: base / stand and service enclosure.','- H: structural head and tablet retention.','- O: optical cassette, service cover, sensor face and film.','- P: one-piece dummy port cartridge.','- V: printed screw / foot instances.','- Q: optional fit and process probes.','- R: reference envelopes, never a print quantity.','', 'Use [fasteners and service](fasteners-and-service.md) for the receiving interface of each V family, [manufacturing workflow](manufacturing-workflow.md) before large prints, and [assembly](assembly.md) for the build order.','', 'This catalog is a file-selection aid. Its bounds and closed-mesh results do not qualify strength, fit, supports or optical performance.']
(r/'docs/part-catalog.md').write_text('\n'.join(lines)+'\n')

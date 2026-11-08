# CAD Provenance, Editable Files and Validation Scope

## Current geometry

- Baseline: native R14 CAD, English-labeled parts and individual STEP exports.
- Amendment: O05 thickness changed from 0.40 mm to 0.20 mm while retaining the optical-film outline and front datum. The amended native assembly is `hardware/cad/native/via-oneplus-pad-r14-1-film-020.FCStd`.
- Current normal assembled Blender scene: `media/via-oneplus-pad-r14-1-assembled.blend`. It is an inspection/render scene, not an editable parametric CAD substitute.
- `hardware/cad/step` contains component-level exchange solids. Reference envelopes are in `references` and must not be printed.
- `hardware/cad/assembly-meshes` uses assembly/world coordinates; printable STLs use proposed print coordinates. Do not substitute one set for the other.

FreeCAD native objects include final B-rep feature shapes. The files permit direct geometric editing, but this should not be represented as a complete sketch-driven parameter tree. Authoring scripts preserve operations from earlier revisions and contain historical application-path assumptions. They are provenance, not a single portable one-click build of every historical revision. The supplied final native CAD/STEP and validated print inventory are the reproducible delivery baseline.

## Historical rationale

R01–R06 explored assembly decomposition, camera/port detail and fit. R07–R11 consolidated monoblock structure, cable/LED routes and root reinforcement. R12–R13 experimented with service/retention concepts. R14 replaced small front snap mechanisms with a top sliding bar and rear integrated locking pins, and separated the detailed optical face from the open carrier for flatter printing. See the full [design report](design-rationale.md). Historical native snapshots and scripts are preserved under `authoring-history`; their original labels/comments are archival and may be Romanian.

## What the reports establish

| Report | Evidence | Does not establish |
|---|---|---|
| print-mesh-audit.json | File hash, triangle count, watertightness, winding and nominal printer-box bounds | Real slicer supports, adhesion, material strength or dimensional fit |
| native-shape-audit.json | Native shape validity/solid counts; explicit O05 amendment dimensions | Physical performance or global absence of every possible collision |
| r14-baseline/geometry.json | Historical native checks of selected changed R14 parts | A full current-assembly print qualification |
| r14-baseline/contacts.json | Selected assembled intersection-volume checks | Fastener strength, retention force or tolerance stack |
| r14-baseline/service.json | Tested H05 displacements and nominal tablet sweep after cover removal | Real bump/buttons/cable sweep, deformation or service life |
| r14-baseline/overhang_screen.json | Triangle-normal screening of selected downward faces | A support-free slicer result |

The 0.20 mm film amendment is smaller in thickness but must still be tested for retention and rattle. Old 0.40 mm reports remain baseline evidence rather than being silently relabeled.

## Re-run STL checks

```bash
python -m pip install trimesh numpy
python scripts/check_print_meshes.py
```

This audits geometry without rewriting meshes. Source checksums and part quantities are in `hardware/parts.json` and `hardware/BOM.csv`. A 256 mm bounding-box check is only a necessary geometric filter; the actual printer profile and support/brim bounds are still decisive.

## Rebuild the publication amendments and gallery

Use a Python interpreter linked to FreeCAD/OpenCascade. Set `FREECAD_LIB` if its Python library directory is not on the interpreter's import path, then run `python scripts/export_cad_amendment.py`. This regenerates the English-labeled native snapshot, the thin-film STEP and assembly mesh, and the native audit. It does not rebuild every historic boolean operation or automatically create a slicer project.

With Blender 4.2 LTS available, run `blender --background --threads 4 --python scripts/render_gallery.py` from the repository root. It uses the archived assembled scene and supplied assembly meshes to produce the current gallery and normal assembled `.blend` inspection file. Material/emission choices are illustrations, not optical measurements.

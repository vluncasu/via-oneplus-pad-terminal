# CAD Files, Editing and Validation Scope

## Current handoff

- [Clean native FreeCAD assembly](../hardware/cad/native/VIA_Terminal_R14_1_Editable.FCStd): only the 30 required printed components, named and grouped by filament.
- [Complete assembly STEP](../hardware/cad/assembly/VIA_Terminal_R14_1_Assembly.step): the same assembled components for exchange with other solid CAD tools.
- [Individual component STEP files](../hardware/cad/step): component-level solids, including explicit reference/probe and alternative variants.
- [Printing files](../hardware/print): quantity-named STLs in their supplied print coordinates.
- [Normal assembled Blender scene](../media/via-oneplus-pad-r14-1-assembled.blend): appearance and mesh inspection.

Use the [direct CAD editing guide](editing-cad.md) to choose a file, modify a local feature and export a revised part. The native files contain final editable B-rep solids; they are not presented as a complete sketch-driven parameter tree. No part-generation macro is needed to open the supplied models.

## Geometry and revisions

Hardware remains R14.1. O05 is 0.20 mm, retaining the original outline and front datum. The engineering native file `via-oneplus-pad-r14-1-film-020.FCStd` retains references/probes; the clean editing file excludes them. The baseline alternative retains the older 0.40 mm film.

Earlier R01–R14 native snapshots are retained in [revision-archive](../hardware/cad/revision-archive). The current handoff contains native CAD and exchange/printing files rather than historical construction source. Earlier revisions are for comparison; select the current R14.1 assembly for a new modification.

Assembly/world-coordinate meshes and STEP files are distinct from proposed-print-coordinate STL files. After editing an assembled solid, choose its print orientation again in the slicer. R01–R05 nominal tablet, supply, USB and LED envelopes are separate [references](../hardware/cad/references), not printable hardware.

## What the reports establish

| Report | Evidence | Does not establish |
|---|---|---|
| [Editable delivery](../hardware/validation/editable-delivery.json) | Native assembly reopens with 30 valid solids; complete STEP round-trip validity/count/volume | Feature-history completeness, real fit or structural qualification |
| [Print mesh audit](../hardware/validation/print-mesh-audit.json) | File hashes, watertightness, winding and nominal printer bounds | Supports, adhesion, material strength or dimensional fit |
| [Native shape audit](../hardware/validation/native-shape-audit.json) | Baseline shape validity and explicit O05 amendment | Physical performance or global collision freedom |
| [Historical reports](../hardware/validation/r14-baseline) | Selected shape/contact checks and nominal service sweeps | Real cable/button/protrusion behavior or service life |

The 0.20 mm film still needs capture/rattle testing. Historical 0.40 mm reports remain baseline evidence. The archive's normal-based overhang screening is not a slicer simulation or a support-free guarantee.

## Check a revised delivery

Measure an imported known dimension, check that each edited solid is valid, export the intended part and inspect the slicer layers. The existing non-modifying mesh audit can be run with `python scripts/check_print_meshes.py` after installing trimesh and numpy. Update the inventory only when the new files and affected interface tests are ready.

The [figure manifest](../media/render-manifest.json) records captions, PNG dimensions and hashes. Images illustrate the supplied component geometry; reference envelopes, section cuts and omitted covers are identified in their captions. See the [verification record](verification.md) and [physical acceptance plan](acceptance-test-plan.md).

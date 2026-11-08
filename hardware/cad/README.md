# Editable CAD — Start Here

## Open this first

**[VIA_Terminal_R14_1_Editable.FCStd](native/VIA_Terminal_R14_1_Editable.FCStd)** is the current assembled terminal with only the 30 required printed components. Parts are named by ID and organized into white, black and natural-PETG groups. It excludes test coupons and reference blocks from the editing view.

| Need | File / folder |
|---|---|
| Modify in FreeCAD | [Clean native assembly](native/VIA_Terminal_R14_1_Editable.FCStd) |
| Open the whole assembly in another solid CAD application | [Complete assembly STEP](assembly/VIA_Terminal_R14_1_Assembly.step) |
| Modify an individual component | [Component STEP files](step) |
| Print an existing component | [Quantity-named, color-separated STLs](../print) |
| Inspect appearance and materials | [Normal assembled Blender scene](../../media/via-oneplus-pad-r14-1-assembled.blend) |
| Measure against nominal tablet/supply/plug envelopes | [Reference STEP files](references) |
| Review earlier native geometry | [Revision archive](revision-archive) |

Follow the [direct editing guide](../../docs/editing-cad.md). CAD dimensions are millimetres. The native assembly contains editable final solids, rather than a complete sketch-driven design tree. STEP is the exchange format for solid editing; STL and Blender are mesh formats.

The component STEP folder root contains 17 unique required file families. Optional probes, thickness alternatives and additional assembled screw instances are in separate subfolders.

## Alternatives and scope

The engineering native file `via-oneplus-pad-r14-1-film-020.FCStd` also retains reference/probe objects. The baseline native file retains the older 0.40 mm film. For a normal clean assembly, use the highlighted file above; current O05 is 0.20 mm.

There are no part-generation macros in this handoff. Historical snapshots are native CAD files. Reference objects R01–R05 are not printed. The [assembly-delivery audit](../validation/editable-delivery.json) checks the new native/STEP exports; it is not a physical fit or manufacturing certificate.

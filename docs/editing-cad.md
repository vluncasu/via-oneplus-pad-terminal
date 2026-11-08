# Modify the Terminal Directly in CAD

## Choose the right format

| Format | Best use | Practical limitation |
|---|---|---|
| FreeCAD `.FCStd` | Open the named assembled solids, measure parts and make local feature edits | Final B-rep solids; not every past dimension is available as a sketch constraint |
| STEP `.step` | Exchange editable solids with another CAD application | Import may produce bodies without an original feature history |
| STL `.stl` | Slice the delivered part for printing | Triangle mesh; a weaker starting point for precise holes, threads and mating surfaces |
| Blender `.blend` | Inspect appearance, cameras, materials and render views | Mesh scene; does not replace dimensionally controlled solid CAD |

Start with [the clean native assembly](../hardware/cad/native/VIA_Terminal_R14_1_Editable.FCStd) or [the complete assembly STEP](../hardware/cad/assembly/VIA_Terminal_R14_1_Assembly.step). Both contain the 30 required printed components in assembled coordinates. There are no coupon blocks or nominal electronics bodies in that clean view.

The printed-components assembly spans approximately **310 × 230 × 341.64 mm**. Use this as a scale check after importing the whole STEP; it excludes the separate nominal tablet/electronics reference bodies.

## FreeCAD editing workflow

1. Save a copy under a new revision before editing. Open the clean native assembly and use Fit All if the model is outside the current view.
2. Expand the filament groups and locate the part by its ID, for example B07 stand/upper cover, H01 front structure or P01 dummy port cartridge. Hide surrounding components to inspect the responsible interface.
3. Measure the existing feature and its mating surfaces. Use the [dimension budget](dimensions-and-clearances.md) and actual component measurements; do not change the entire scale to fix one clearance.
4. For a local hole, cutout or extra support, use the application's solid feature/Boolean tools. In FreeCAD, a Part Design Body can use the selected solid as its BaseFeature where supported; add a sketch and feature to that body. For a different workflow, use Part solids and Boolean operations. Save the original part as a comparison reference.
5. Keep a counterpart visible while checking a mating surface. Preserve the cable duct, LED seat, service removal path and adjacent screw engagement. A visually smooth exterior alone does not establish fit.
6. Check the edited solid for shape errors, then export that part as STEP for exchange and as STL for the slicer. Keep its ID and mark the new revision so it cannot be confused with an unchanged release file.
7. Orient the new STL in the slicer intentionally. The clean native/assembly STEP uses **assembly coordinates**; it does not preserve the supplied print orientation automatically. Check units, bed bounds, supports and modeled empty regions.
8. Print a local fit sample or the appropriate probe before replacing the large component. Repeat the checks affected by the change.

Imported final solids support additional features, but changing an existing fillet, shell or coarse thread may require direct face editing or rebuilding that region. Do not assume a complete parameter tree exists simply because the file is native FreeCAD.

When changing a repeated screw family, check every matching receiving thread and update each affected instance in the assembly. The clean assembly contains independent solid instances; a change to V21 does not automatically propagate to V22–V24.

## Other solid CAD applications

Import the complete STEP when you need assembly context. Import one component STEP when you need a lighter workspace. Confirm millimetres, part count and a known dimension after import. Keep bodies separate, then use the application's supported direct-edit or feature workflow. Save in that application's native format before experimenting.

The STEP folder root contains the 17 unique required component families. Probe models, thickness alternatives and repeated screw instances are in separate subfolders. Use the [part catalog](part-catalog.md) to identify the 17 unique required file families; current O05 is the explicitly named 0.20 mm film, not the 0.40 mm baseline alternative.

## Changes that require a paired check

| Change | Check before printing the whole part |
|---|---|
| B07 stand root | Load path into the cover, supply access and uninterrupted cable duct |
| H01 tablet opening | Actual corner/body fit, original front camera, H05 guide engagement |
| H05/H06 guides or pins | Locked restraint and the complete unlocked upper-rear extraction path |
| Optical carrier / film seat | Forward and rearward capture, O03 closure and USB access |
| P01 port face or funnel | Base recess, cartridge retention and actual incoming-cable bend |
| LED seating | Strip width/height, permitted corner bend, feed joint and closing screws |
| Printed screw / receiving thread | Matching coupon fit, engagement length and supported thread seat |

For new clearances, prefer a local interface change rather than global scaling. Slicer infill does not create a designed void: the duct and LED clearance must remain actual empty geometry. See the [manufacturing workflow](manufacturing-workflow.md) and [acceptance plan](acceptance-test-plan.md).

## Blender and printing

The normal Blender scene remains assembled and can be edited visually without running a generation script. Select objects by part ID, change materials/cameras and render through the interface. Use native/STEP solids for dimensionally controlled mechanical edits. The existing color-separated STL set is the direct printing starting point when no design change is needed.

# CAD Files and Editing

## Choose a file

| Purpose | File or folder |
|---|---|
| Edit the assembled terminal in FreeCAD | [Clean native assembly](../hardware/cad/native/VIA_Terminal_R14_1_Editable.FCStd) |
| Open the complete assembly in another solid CAD application | [Assembly STEP](../hardware/cad/assembly/VIA_Terminal_R14_1_Assembly.step) |
| Edit one component | [Individual STEP files](../hardware/cad/step) |
| Print the supplied components | [STLs by filament color](../hardware/print) |
| Change appearance, lighting or camera views | [Assembled Blender scene](../media/via-oneplus-pad-r14-1-assembled.blend) |
| Compare earlier designs | [Native revision archive](../hardware/cad/revision-archive) |

The clean FreeCAD assembly contains the 30 required printed components, grouped by filament and named by part ID. The complete STEP contains the same assembled components. The component STEP folder root contains 17 unique required families; optional probes, thickness alternatives and additional screw instances have separate subfolders.

## Edit directly

Follow the [CAD editing guide](editing-cad.md). The native files contain final editable B-rep solids. They support direct solid edits and additional features, but do not provide a complete sketch-driven parameter tree for every earlier operation.

Use millimetres and check a known dimension after import. STEP and the native assembly use assembled coordinates. The supplied printing STLs use their proposed print orientation; choose orientation again when exporting a newly edited solid.

## Select the current revision

Current hardware is R14.1, including the O05 0.20 mm optical film. The 0.40 mm film is a separate alternative. The engineering native file retains reference and probe bodies; the clean editing assembly excludes them. Nominal tablet, supply, plug and LED envelopes are in [references](../hardware/cad/references) and are not printable hardware.

Keep the [BOM](../hardware/BOM.csv) and [part catalog](part-catalog.md) beside the model. After changing a joint, check its counterpart, the cable route, the LED seat and the service-removal path before printing the complete replacement. See the [assembly guide](assembly.md) and [acceptance plan](acceptance-test-plan.md).

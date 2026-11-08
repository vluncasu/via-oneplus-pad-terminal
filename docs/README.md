# VIA Engineering Documentation

This handbook connects the **OnePlus Pad OPD2203 enclosure** to its printable components, assembly interfaces and offline Android demonstration. Hardware revision remains **R14.1**; this documentation expansion does not change the STL geometry or APKs.

[Download the illustrated handbook PDF](VIA_Assembly_and_Demo_Handbook.pdf) for the offline assembly/demo reference. The separate [engineering report](VIA_Engineering_Design_Report.pdf) develops the design rationale.

[Expanded offline downloads](https://github.com/vluncasu/via-oneplus-pad-terminal/releases/tag/r14.1-docs.2) · [Edition changes](documentation-changelog.md)

## Choose your task

| Task | Read first | Use alongside it |
|---|---|---|
| Understand the object | [Design rationale](design-rationale.md) | [Product views](gallery-product.md) |
| Identify every part and quantity | [Part catalog](part-catalog.md) | [Color-separated files](../hardware/print) |
| Decide what to print first | [Manufacturing workflow](manufacturing-workflow.md) | [Printing settings](printing.md) |
| Understand joints and tablet retention | [Interfaces and retention](interfaces-and-retention.md) | [Engineering views](gallery-engineering.md) |
| Assemble without losing access | [Illustrated assembly](assembly.md) | [Fastener map](fasteners-and-service.md) |
| Install LED strips and internal leads | [LED and wiring](led-and-wiring.md) | [Dimensions and clearances](dimensions-and-clearances.md) |
| Run the ten-minute demonstration | [Demo runbook](demo-runbook.md) | [Software architecture](software.md) |
| Diagnose a problem | [Troubleshooting](troubleshooting.md) | [Acceptance and test plan](acceptance-test-plan.md) |
| Audit a design claim | [Requirements traceability](requirements-traceability.md) | [Verification record](verification.md) |
| Edit or reproduce the design | [CAD provenance](cad-and-validation.md) | [Native CAD](../hardware/cad/native) |

## What each evidence label means

**Modeled** means the feature exists in the supplied shape. **Digitally checked** refers to a named report or build/test result. **Trial procedure** is an instruction for a future physical check. **Reference envelope** reserves space; it is neither a real component model nor a promise that a purchased component fits. Keep these distinctions when presenting the project.

Required color batches are 25 white PETG pieces, 4 black PETG pieces and 1 natural PETG film. These are quantity totals, not numbers of separate STL files.

The normal Blender file opens as an assembled terminal. Isolated, cover-omitted and sectioned figures are supplementary inspection views. No illustrated cutaway is an STL modification. Parts marked R01–R05 are reference envelopes and are not printed.

## Version and scope

- Application source / official demo APKs: 1.0.5.
- Mechanical baseline: R14; O05 optical film amended to 0.20 mm in R14.1.
- Required print set: 17 unique files, 30 printed pieces; 15 optional probes.
- Runtime: local tablet and phone, with a QR request and BLE response; no external backend.
- Actual printing, tablet fit, load capacity, temperatures and radio/camera behavior require physical qualification.

Start with the low-material probes and an unpowered dry build. Keep the same part IDs in your slicer project, build notes and test photographs so a failed interface can be traced to an actual file.

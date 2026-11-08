# 3D Printing the OnePlus Pad Enclosure

Read the [staged manufacturing workflow](manufacturing-workflow.md) before committing the largest jobs. Use the [part catalog](part-catalog.md) for exact file quantities and exported bounds.

## Select files

Use `hardware/print/white-petg`, `black-petg` and `natural-petg`. Every filename begins with a quantity and stable part IDs. For example, `04x_V21-V22-V23-V24_...stl` means print that geometry four times. The 17 required files make 30 physical items. Fifteen optional test files are separate. Do not print R01–R05 reference envelopes. The `alternative-thickness` O05 file is an alternative, not an additional required item.

The publication does not arrange build plates or provide G-code. Import parts individually, retain their proposed orientation, and inspect the actual printer profile before committing a job.

## Material and trial settings

| Group | Starting point | Why / limitation |
|---|---|---|
| White structural PETG | 0.16–0.20 mm layers, 5–6 perimeters, 15–25% gyroid | Starting trial only; ribs and perimeters carry the intended load paths |
| Stand root, head mount and screw seats | Local denser modifiers and more continuous walls | Select after coupons/load tests; do not apply uniform 100% infill to all large parts |
| Black dummy port and sensor details | 0.08–0.12 mm layers, slow outer walls | A 0.4 mm nozzle cannot resolve arbitrary sub-nozzle details |
| O05 natural PETG film | First layer **0.20 mm**, total height **0.20 mm** | Preview must show exactly one layer; no support, raft or attached brim on the optical outline |
| O05 alternative | Two 0.20 mm layers | Choose instead of the default if a thicker film is needed; recheck retention |
| Printed threads | Upright axis as supplied, well-calibrated flow | Print clearance coupons before all repeated screws; never force an uncalibrated thread |

Use filament-specific temperatures, drying and bed preparation. Natural/translucent PETG is not guaranteed optically clear. The currently published rigid screw feet are PETG, not TPU anti-slip pads. Electronics, strip, wiring and tablet are purchased functional components.

## Orientation and support rationale

- H01/H04: edge-on, diagonal. The approximately 242.75 mm head projection fits the nominal 256 mm square, leaving limited room for brim/supports. Confirm bed exclusions and stability in the slicer.
- H05: front face down, diagonal; side guide ramps avoid small spring arms.
- H06: exterior rear face down; integrated locking pins rise from the plate.
- O06: flat back down, decorative details upward.
- O01: front rim down, open cavity upward. Internal thread flanks, bridging and side USB opening still need inspection.
- B07: supplied monoblock orientation; check the internal cable duct and reinforcement roofs, not just the external silhouette.
- B01/B03: retain the provided orientation until the geometry is understood; their bounds are not necessarily their unrotated assembled dimensions.

Supports must never fill the cable duct, LED channels, dummy sockets or optical retention seat. Use explicit support blockers/paint where appropriate. The historical normal-based overhang screen is not a slicer simulation and is not a support-free guarantee.

## Coupons first

Print only the tests you need: Q07 tablet corner; Q11 front-camera clearance; Q12 USB body pull-through; Q13/Q14 259.03/190.41 mm opening gauges; Q01–Q06 thread clearance; Q08–Q10 wall transmission; Q15 LED-channel corner. These inherited coupons do not validate all R14 locking guides. Make a local segment of any new critical joint before printing the complete head.

## Infill and finishing

CAD voids are intentional geometry. Keep the cable duct, electronics cavity, service opening, LED seating volume and vents empty. Infill applies only inside the remaining closed shells. Check every layer around the stand root and thread-bearing bridges. Increase local material where load crosses interfaces; a high infill percentage cannot repair a thin or poorly oriented attachment.

Test assembly before sanding and paint. Keep threads, guides, clearances and luminous zones masked. Avoid aggressive chemical smoothing near dimensional datums. No mass, print time or filament-consumption promise is made without a slicer profile and chosen material.

Use the [BOM](../hardware/BOM.csv), [part catalog](part-catalog.md) and [assembly guide](assembly.md) alongside the print files.

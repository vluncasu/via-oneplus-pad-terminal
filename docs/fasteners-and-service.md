# Printed Fasteners and Service Map

The current assembly uses printed screw families rather than purchased bolts or heat-set inserts. These coarse printed threads are not standard ISO metric hardware. Do not substitute a similarly named metal M8 or M12 bolt without redesigning its mating geometry.

## Screw families

| IDs / copies | Function | Nominal file designation | Service access |
|---|---|---|---|
| V21–V24 / 4 | Head-to-stand structural attachment | D12, pitch 2.5, L12 | At the head interface with service access |
| V31–V34 / 4 | Spherical slotted feet | D8 screw foot | Underside; slot must remain accessible |
| V41–V44 / 4 | Bottom service cover | D8, pitch 2.5, L10 | Upward from the underside |
| V51–V54 / 4 | Rear head covers / stops | D8, pitch 2.5, L14 | Rear face; upper pair V52/V54 releases H06 |
| V61–V62 / 2 | USB optical service cover | D8, pitch 2.5, L16.3 | O03 service region |

File designation is a nominal CAD identifier, not a measured fit or a tightening-torque rating. The full part filenames and quantities are in the [catalog](part-catalog.md).

## Fit before force

Print Q01–Q06 using the intended filament, orientation and layer height. Clean the thread start, start square by hand and test repeated insertion into the coupon. Choose a working clearance before making the full screw batch. Use a driver that fits the printed slot and apply gentle hand force; do not use a powered driver or use screw torque to close a misaligned housing.

Check that the screw actually engages the receiving thread, rather than just resting in a cosmetic recess. A rear screw should seat at its intended exterior datum. If it remains proud, inspect debris, wrong family, bottoming length and cover alignment. Grinding the cap flush without checking engagement can remove useful material while leaving the joint loose.

| Symptom | Inspect before changing dimensions |
|---|---|
| Thread will not start | Wrong family, tilted start, elephant foot, seam blob, calibrated clearance |
| Head seats but joint moves | Mating faces, actual thread engagement, premature bottoming, stripped receiving wall |
| Cover distorts while tightening | Cable beneath the cover, support remnant, wrong screw length or interface mismatch |
| Foot loosens repeatedly | Fit, cyclic rotation and desk friction; rigid PETG feet are not anti-slip TPU |
| Thread cracks its seat | Layer direction, wall continuity, local web geometry and excessive tightening |

## Service without dismantling everything

| Task | Open first | Preserve |
|---|---|---|
| Unplug tablet charging | O03, V61/V62 | Optical film and tablet front glass |
| Remove tablet | O03, then H06 / V52/V54, then H05 | Support tablet while the top restraint is released |
| Inspect low-voltage distribution | Bottom cover B03 / V41–V44 | Stand-bearing interface and root braces |
| Inspect optical capture | O03 and the service side of O01, with tablet protected | H01 shoulder and film outline |
| Inspect port cartridge | Bottom service access | Exterior base wall and cartridge recess |

Keep a labeled tray with one compartment per screw family. Reusing the wrong D8 length can bottom out even when the diameter appears correct. Interior part IDs and filename quantities are the primary assembly references. Do not add visible labels or permanent filler over service seams.

No fatigue life, pull-out capacity or torque specification has been established. Inspect printed threads after warm operation and after repeated service; replace damaged pieces rather than forcing them.

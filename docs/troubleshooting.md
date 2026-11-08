# Troubleshooting by Symptom

Identify the responsible interface before sanding, scaling or tightening. Keep the part ID, actual file revision and a photograph in the build note.

## Printing and mechanics

| Symptom | Inspect | Corrective direction |
|---|---|---|
| Slicer shows infill in cable route | Import units, mesh interpretation, repair result, supports versus infill | Compare with duct-section figures; preserve the real CAD void |
| Head fits nominal box but not the printer preview | Brim/support extents and exclusion zones | Review diagonal placement and adhesion; do not crop a structural part to fit |
| Print needs inaccessible supports | Orientation and roofs inside carrier/duct | Reorient or revise the responsible feature before a full print; do not entomb support |
| Tablet opening seems too small | Actual dimensions, corner shape, first-layer/paint effects | Use gauges and local fit correction; avoid globally scaling all joints |
| H05 will not slide | H06 still engaged, guide burrs, paint, orientation | Remove H06 first, support tablet, inspect guide clearance |
| Tablet can move with covers closed | Stops, H05 seating, H06 pin engagement, wrong screw | Inspect complete restraint chain; do not pad the screen with a cable |
| Optical face or film falls forward | Correct stack, H01 shoulder, carrier seating, film thickness | Refit and test capture without the tablet; reject a loose assembly |
| P01 projects or moves outward | Recess seating, debris, service closure, mating contact | Measure actual interference/gap; revise cartridge/interface rather than leaving it proud |
| Stand rocks at root | Bearing face, burrs, layer damage, wrong screw family | Unload, inspect and correct fit; extra torque is not reinforcement |
| A screw cap is flush but joint is loose | Thread engagement, premature bottoming, stripped seat | Confirm receiving thread is doing work; replace damaged pieces |
| Fine vent lattice disappears | Minimum printable feature width and slicer line generation | Use actual preview and a local sample; a CAD line is not a printed strand |
| One-layer film lifts or has holes | First-layer height, cleanliness, flow and bed adhesion | Calibrate the 0.20 mm single layer; keep the outline undamaged |

## LED and charging

| Symptom | Inspect | Corrective direction |
|---|---|---|
| Strip cannot turn a corner | Bend direction/radius, PCB construction, components | Follow actual strip data; plan accessible allowed cut/feed joints |
| Feed joint collides with a screw | Corner feed placement and service slack | Route around the bearing/thread region before closure |
| Whole white shell glows | Filament opacity, wall thickness, seams and finish | Test transmission coupons and a compatible masking/design solution |
| Belt is uneven | Strip-to-wall geometry, corners and joints | Test exact parts/strip; renders are not a luminance measurement |
| Tablet does not charge reliably | Supply voltage/protocol, cable, plug seating and strain | Verify the real charging chain outside the enclosure first |
| Temperatures keep rising | Actual strip power, carrier requirements, closed airflow | Stop the test and review the thermal design/component documentation |

## Tablet and phone

| Symptom | Inspect | Corrective direction |
|---|---|---|
| New profile is not in Experiences | Enrollment completion and local save | Finish the full named flow; compare actual list after restart |
| Phone scan does not complete tablet | Bluetooth, Nearby devices, QR expiry, matching session | Enable both adapters, grant permissions, refresh/scan the current code |
| Retry after Bluetooth enable still stalls | Adapter fully on, phone timeout, stale session | Retry on both sides as needed; generate a fresh QR after expiry |
| Phone Back exits unexpectedly | Installed app version/signature | Use official 1.0.5 and retest from its result screen |
| Official APK will not update | Existing package ID, signing key, Android install error | Do not mix CI and official signatures; protect local data before uninstalling |
| Face/palm indications are weak | Real camera obstruction, lighting, distance, permissions | Correct the camera setup; decorative lenses are not detectors |
| Internet is absent | BLE and local permissions, rather than Wi-Fi | The app requires no server; keep Bluetooth enabled for confirmation |
| Android notifications appear | Device-level presentation configuration | Use OS DND/settings; immersive UI is not a proven Device Owner kiosk |

See [demo runbook](demo-runbook.md) and [physical acceptance plan](acceptance-test-plan.md) for the expected successful sequence.

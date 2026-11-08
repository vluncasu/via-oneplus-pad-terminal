# Requirements-to-Evidence Matrix

This matrix condenses the design decisions and corrections that shaped VIA. “Present in CAD” and “physically validated” are deliberately different statuses. Hardware remains R14.1; the expanded figures explain the delivered geometry rather than inventing a further redesign.

| Requirement | Delivered mechanism / artifact | Evidence and remaining check |
|---|---|---|
| Fits OnePlus Pad OPD2203 | Nominal body envelope, H01 pocket, Q07/Q11/Q13/Q14 | Native CAD and gauges; actual tablet fit/camera still required |
| Original front glass; no obvious tablet clamps | Structural surround and rear stops | Product/front views; inspect screen overlap and camera on device |
| Tablet removable through upper rear | H05 sliding bar and H06 integrated locking pins | Historical service sweep and figures 20/21/29; real removal test |
| Continuous one-piece S stand | B07 integrates stand and upper power-volume cover | One required B07 STL; layer/load/creep tests pending |
| Reinforcement belongs to the stand | Integrated root braces | Figures 09/23; structural load qualification pending |
| Cables hidden through the stand | Explicit modeled duct | Figures 10/30 and Q12; actual plug plus LED leads must pass |
| Monoblock outer base | B01 | Required STL; trial seam and cartridge seating |
| Bottom service access | B03 / V41–V44 | Figure 24 and service map; actual service access check |
| No added visible top screw holes | Underside-access base assembly | Assembled views and CAD; verify actual screw seating |
| Integrated head/base LED channel structures | H01 and B01 | Figures 07/08; no L1/L2 items in print inventory |
| 8 mm LED plus allowance | 8.5 mm nominal reserved width | Q15; actual bend, solder joint and thermal needs |
| Light only at intended belt | Integrated rim/shield geometry, about 3 mm belt | Optical transmission intent; leakage/brightness test pending |
| More realistic black dummy ports | One P01 cartridge, recessed | Figures 04/25/26; visual and retention checks |
| No projecting port plate | Base recess and cartridge position | CAD/product views; printed tolerance and closure check |
| Complex dummy sensor appearance | Separate black O06 face inside O01 | Figures 11/27/33; printed detail depends on nozzle/settings |
| Captive optical face / film | H01 shoulder, carrier relationship and O03 service access | Figure 27; verify capture in both directions after printing |
| One-layer optical film | O05 0.20 mm, original outline preserved | Native amendment and STL audit; adhesion/retention trial |
| No tiny loose lock pin | H06 pins integral to cover | R14 source and service map; printed pin engagement test |
| Printable fasteners | Coarse D12/D8 screw families | Thread meshes/coupons; no ISO metric or torque claim |
| Hidden part identification | Stable IDs and interior marks | Catalog and native labels; ensure marks survive slicing/finish |
| Minimal-support strategy | Open O01, flat-backed O06, guided bar without snap arms | Supplied orientation; actual slicer support review pending |
| All structural/dummy parts printable | Color/quantity inventory | 32 audited STL files; electronics remain real components |
| No plate arrangement | Individual STL files by color | Print folder and release archive |
| Entire demo local | No INTERNET permission; local profiles and QR/BLE | Build/manifest checks; actual device interoperability test |
| No instant payment/validation | Bounded signed request/response flow | Protocol tests and demo runbook |
| Multiple named profiles | Atomic save, complete local list | Persistence/UI tests; restart check on tablet |
| Correct retry / Mobile Back | Adapter retry handling; Home navigation | Regression tests; lifecycle/radio checks on devices |
| Inspect a normal assembled model | Delivered English-labeled Blender scene | Opens assembled; sectioned figures are separate illustrations |

Source artifacts: [CAD provenance](cad-and-validation.md), [verification](verification.md), [part inventory](../hardware/parts.json), [software](software.md). There is no claim of a certified payment system, dust filter, thermal rating or secure biometric identity.

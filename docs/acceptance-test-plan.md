# Assembly Acceptance and Physical Test Plan

These are **proposed build-qualification procedures**, not completed test results. The [verification record](verification.md) names the checks actually executed. Record part revision, material, print profile, actual electronics and ambient conditions with every result.

## Gate A — Before large prints

| Check | Method | Acceptance for the next stage |
|---|---|---|
| File scale | Import one known part and compare its bounds with the catalog | Millimetres and expected dimensions; no accidental unit scaling |
| Thread choice | Run the matching clearance coupons | Hand-start and repeated seating without damage |
| Tablet corner/opening | Fit actual tablet to Q07/Q13/Q14 | No forced glass contact; dimensions recorded |
| USB connector | Compare actual molded body with Q12 | Complete plug is represented; bends still to be checked in assembly |
| LED corner | Fit exact strip to Q15 | Width, package height and corner-feed strategy are workable |

## Gate B — Unpowered complete dry assembly

1. Assemble B01/B07 and the head without live electronics. Confirm bearing faces seat before tightening.
2. Pass the actual charging connector through the complete internal route. Add the LED leads; repeat. Inspect both ends for pinch points with covers temporarily fitted.
3. Insert P01 and close the service assembly. Check that it remains recessed and cannot move outward under gentle handling. Do not insert a real plug into the decorative sockets.
4. Fit O01/O06/O05 and O03. With the tablet protected or absent, check capture from front and back. Reject loose films or faces that can fall out.
5. Fit the tablet without USB tension, close H05/H06, and confirm that stops bear on intended body regions. Check buttons, screen edges and front camera.
6. Repeat the documented upper-rear removal and reinstallation. Count any burr removal or adjustment; a screw should not be needed to pull a distorted cover into alignment.
7. Inspect all visible screw seating and the driver access to the spherical feet. Check whether the assembled base rocks on a flat desk.

Acceptance is successful operation of every relevant interface without damage, unintended preload or lost access. This procedure does not establish load capacity.

## Gate C — Structural behavior

Support and restrain the prototype so the tablet cannot fall during testing. Begin with the intended dead load and a substitute mass if the real tablet is at risk. Observe stand-root deflection, the head joint, printed thread seats and the base after assembly. Evaluate touch forces and cable pull progressively, using measured loads selected for the intended use. Stop if a joint moves, a layer whitens/cracks or deformation grows.

Record force, application position, direction, duration and deflection; repeat after warm operation and after service cycles. Define the required load cases and allowed deformation before qualification. The illustrative moments in the design rationale are not passed test loads and no safe structural rating is assigned here.

## Gate D — Powered closed-assembly behavior

Use the actual component documentation to establish supply, cable and LED limits. Start at a controlled low LED setting. Log strip/support, power-electronics and tablet-region temperatures in the closed assembly, including ambient conditions and time. Continue until the relevant temperatures stabilize under the intended use. Inspect for light leakage, charging interruptions and heat-induced movement.

A pass requires remaining within the applicable component/material limits and preserving mechanical fit and function. This repository does not specify a universal plastic-safe strip wattage or authorize an unverified mains installation. An open-bench ten-minute light test is not the closed-enclosure thermal test.

## Gate E — Actual tablet / phone

| Scenario | Expected behavior |
|---|---|
| One completed new enrollment | Exactly one named local profile appears |
| Three completed enrollments then app restart | All three records remain visible in Experiences |
| Open payment or validation QR | Request/waiting state; no immediate paid/valid result |
| Scan using Mobile with Bluetooth enabled | Response reaches the matching tablet session and result is accepted |
| Disable then re-enable tablet Bluetooth | Clear retry path; no stale attempt is accepted as a fresh confirmation |
| QR expiry followed by new request | New code is required; an old session must not complete the new one |
| Press Back after Mobile success | Home, rather than an unintended app exit |
| Internet unavailable, Bluetooth enabled | Local QR/BLE path remains available |

Automated protocol tests support some state logic; they do not replace radio, permission, camera or Android lifecycle checks on the actual devices.

## Test record template

Copy this into a build note for each gate:

- Date / operator / hardware revision / exact STL or native source.
- Printer / nozzle / filament / drying / layer height / orientation / walls / infill modifiers / supports.
- Actual tablet, phone, cable, LED and supply identifiers.
- Procedure and measured conditions.
- Observations, photographs and pass / fail / not tested.
- Corrective action and the revision that must be rechecked.

Do not replace a failed measurement with a render. Attach the evidence to the part IDs so future revisions can be compared.

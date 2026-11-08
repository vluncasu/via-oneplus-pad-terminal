# Manufacturing Workflow and Print-Preparation Gates

Use this sequence to avoid committing the largest prints before the interfaces are understood. It is a trial workflow for the published meshes, not a prevalidated printer profile. The [catalog](part-catalog.md) lists the actual supplied STL bounds, which can differ from assembled dimensions because parts are rotated for printing.

## 1. Establish the reference components

Record the actual tablet width, height, body thickness, corner shape, rear camera protrusion, button positions and front-camera field of view. Record the complete USB-C plug body including strain relief and any right-angle projection. Measure the supply body and the additional space needed for terminals, connectors and cooling. A 92 × 64.02 × 39.02 mm CAD block is not a mounting drawing for every 12 V supply.

Keep an unmodified copy of the release files. Import in millimetres and check a known dimension before changing orientation or scale. A near-fit should be corrected at the responsible interface, not by uniformly scaling the terminal and changing every thread and seat.

## 2. Print the smallest useful evidence

| Question | First probe | What constitutes a useful result |
|---|---|---|
| Will the tablet corner and thickness seat? | Q07 | Real corner seats without glass pressure; rear protrusions remain accounted for |
| Is the whole opening large enough? | Q13 and Q14 | Actual body clears both gauges; they do not establish all corner/button clearances |
| Is the front camera unobstructed? | Q11 | Preview has no edge obstruction in the intended mounting position |
| Can the cable body pass through? | Q12 plus the actual unpowered cable | Both pass the complete route; a straight gauge alone does not establish a bent route |
| Which thread clearance works? | Q01–Q06 | Starts by hand, seats repeatedly, does not strip or bind |
| Which wall transmits acceptable light? | Q08–Q10 | Compare with the exact strip and filament under the intended room lighting |
| Does the strip corner fit? | Q15 | Width, package height, bend direction and feed joint all fit |

These coupons are inherited checks. H05/H06 guide and pin engagement still need a local joint sample or a careful first complete dry build. A successful Q12 print is not proof that every USB-C cable is compatible.

## 3. Prepare each structural job

Inspect the contact face on the plate and the highest bridge in the slicer. H01/H04 use an edge-on diagonal strategy; B01/B03 supplied files also have deliberate rotations. Keep the proposed orientation until supports, cooling and bed exclusions have been reviewed. B07 is a single-piece stand plus upper power-volume cover, so a print failure near its root affects the whole part.

Use the [printing guide](printing.md) for trial layer heights and walls. Start with the filament maker's profile, calibrate flow and dimensional behavior, and inspect the first layers before leaving a long job. Add supports only after checking whether they can be reached and removed. Do not seal support inside the stand duct, LED grooves or optical carrier.

## 4. Distinguish CAD voids from slicer infill

The stand duct, supply cavity, LED seating regions and service openings are modeled empty regions. They are not low-density infill regions. In the layer preview they must remain empty, except for explicitly generated supports that can be removed. If infill appears in the duct, inspect the imported mesh interpretation and any repair operation before continuing.

The structural shell surrounding those voids receives perimeters and infill. For a first trial, use the guide's 5–6 walls and 15–25% gyroid, then review local modifiers at the stand root, head interface and thread seats. Use continuous material around a threaded boss and its supporting web. Avoid a tiny dense cylinder disconnected from the surrounding wall; density alone does not make a load path.

| Region | Preserve | Inspect in layer preview |
|---|---|---|
| B07 stand root | Braces, radiused transitions and duct walls | Continuous layers into the upper cover; no support trapped in the duct |
| H01 stand interface | Thread seats and their connecting material | More than isolated towers; no LED feed in the bearing region |
| LED channels | Seating and optical rims | Strip clearance, corner transitions and accessible feed point |
| Fine vents | Thin concealment geometry and open flow paths | Features are resolved by the 0.4 mm nozzle rather than silently omitted |
| O01/O06 optical parts | Flat printing surfaces and captive shoulder relationship | Open carrier; details upward on O06; no large roof across its cavity |

## 5. Print optical and repeated parts

Print O06 black with its flat back down. Keep detail surfaces upward; begin at 0.08–0.12 mm layers and check whether narrow features survive the preview. O01 is the open carrier, not a closed sensor box requiring a roof full of supports. P01 is one black cartridge containing all dummy ports.

Print O05 natural PETG at **0.20 mm first layer and 0.20 mm total height**. The preview must contain exactly one layer. Do not add a raft or optical-face supports. Keep the 0.40 mm alternative separate; it is not a second required film. Printed PETG film will not reproduce the optical quality of glass.

Only print all repeated screws after a thread probe is usable. Filename quantity is the count of copies of that geometry; for example, four copies of the V21-family file provide V21–V24 in total.

## 6. Finish, inspect and record

Remove burrs without rounding away guides or thread starts. Trial assembly before filler, sanding or paint. Mask threads, locating faces, luminous zones and the film seat. Record material, nozzle, layer height, wall count, local modifiers, support strategy and orientation for each successful part. Slicer estimates are the source for actual filament use and print duration; CAD solid volume is not a spool estimate.

Proceed to the [assembly sequence](assembly.md), then sign off the [acceptance checks](acceptance-test-plan.md). Keep failed probe settings in your notes: they explain which clearance and material combination was rejected.

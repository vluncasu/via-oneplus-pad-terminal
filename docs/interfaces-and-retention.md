# Mechanical Interfaces, Retention and Load Paths

The assembly has three different jobs: carry the tablet's loads, retain service parts, and hide decorative details. A locating surface positions a part; a threaded joint retains it; neither should rely on trapped wiring. The [engineering gallery](gallery-engineering.md) shows these relationships with selected covers omitted.

## Structural chain

```mermaid
flowchart LR
    T[Tablet body] --> H[H01 structural frame and rear stops]
    H --> J[Head-to-stand bearing interface / V21–V24]
    J --> S[B07 continuous S stand]
    S --> R[Integrated root and braces]
    R --> B[Upper power-volume cover / B01 base]
    B --> F[Four printed feet]
    F --> D[Desk]
```

This is the intended load path, not a structural calculation establishing capacity. The power-supply reference is not a brace and must not support the stand by accidental contact. The root reinforcement belongs to B07. It should transfer force into the broad cover while preserving both the explicit duct and the intended electronics space.

## Base and power-volume cover

B01 is the monoblock outer base. B07 integrates the upper volume and the one-piece S stand. B03 closes the service side underneath. The outer interfaces should seat before their fasteners are tightened. The top finish is not a place to add compensating screw holes. Feed wires and the cartridge are installed while the underside remains accessible.

The underside view with the orange block depicts R02, a provisional supply envelope. It makes the conflict between reinforcement, component space and access visible. It does not represent terminal clearance, mains isolation or thermal certification of an actual supply. Verify these with the selected low-voltage power system and its manufacturer's instructions.

## Head-to-stand connection

The head is attached by the V21–V24 family of coarse D12 printed screws at the matched interface. Check that all intended bearing faces contact evenly. If the joint rocks while a screw is loose, inspect burrs or a geometric mismatch; tightening harder is not a corrective alignment method. Keep the internal cable passage open across this connection and pull the cable through before final closure.

A visible junction line is a service interface. It should remain narrow and consistent, without a projecting bracket being mistaken for extra stand width. This publication depicts the actual R14 interface; it does not replace its geometry with a seamless artistic blend in the renders.

## Tablet restraint and upper-rear service

H01 surrounds the original tablet face, while rear covers/stops control rearward movement. The actual tablet's own front glass remains exposed. The frontal camera opening belongs to the actual camera position, not to the decorative side sensor bar.

H05 is a sliding top retention bar. Its open guides constrain it through the depth direction while permitting the intended upward removal path once unlocked. H06 is the upper rear service cover. Its **integrated straight pins** enter H05 receivers and block the bar's lifting path when the cover is fully seated. The rear screws retain H06. These pins are not a flexible snap mechanism and there is no separate tiny pin to install.

| State | Parts present | Intended outcome |
|---|---|---|
| Closed | H05 guided, H06 seated and rear screws installed | Bar cannot simply lift out; upper stops retain the tablet |
| Service cover removed | H06 withdrawn, tablet supported | Integrated pins clear H05; bar can follow its guide path |
| Extraction | H05 removed, USB-C unplugged, tablet supported | Tablet leaves through the upper rear service opening |

Do not test removal by pulling on the tablet while the service cover is fitted. First support the assembly, disconnect USB-C through O03, undo the two upper rear screws, withdraw H06, then lift H05 in its screen plane. The archived sweep report is only a nominal geometric sweep: real camera protrusions, buttons, cable stiffness and printed deformation are excluded.

## Captive optical assembly

O01 is the black open carrier. O06 is the separate flat-backed decorative face. O05 is the 0.20 mm film, captured against the shoulder integrated into H01. O03 closes the USB service region using V61/V62. The structural shoulder and assembled carrier relationship are intended to prevent a forward fall; the printed film is not an adhesive structural retainer.

Test capture from both sides during the dry build. With the tablet absent, gently check whether the film, face or carrier can leave its intended seat. The thinner R14.1 film has a different flexibility from the original 0.40 mm film, so clearance and capture must be verified again. If it falls forward, the assembly is not accepted merely because the render appears flush.

The side cassette hides the **USB-C connector and cable**, not the whole charger. Its dummy lenses, recesses and sensor-like relief are decorative. The functional face/smile/palm camera is the tablet's front camera.

## Recessed port cartridge

P01 is one black printed part with the dummy connector internals and real cable funnel. It is inserted through the service side into the base's recessed opening. Check recess depth, locating contact and closure of the bottom assembly before judging retention. Do not depend on a friction fit whose behavior has not been measured. If the cartridge can move outward after closure, record the actual contact gap and revise the responsible retaining geometry.

Real electrical connectors are not formed by the printed dummy features. Their internal tongues/cavities create depth and visual detail. Avoid testing them with a real plug; thin printed features may break or trap it.

See [fasteners and service](fasteners-and-service.md) for screw families and [acceptance checks](acceptance-test-plan.md) for practical verification.

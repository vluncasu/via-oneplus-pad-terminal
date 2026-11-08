# Dimensions, Datums and Clearance Budget

All dimensions are millimetres. Values below distinguish manufacturer body dimensions, nominal CAD envelopes and unvalidated allowances. A CAD clearance is not automatically a usable manufacturing tolerance.

| Feature | Value / interpretation | Source and verification needed |
|---|---|---|
| OnePlus Pad OPD2203 body | 258.03 × 189.41 × 6.54 | Manufacturer nominal; measure the actual tablet and protrusions |
| H01 head envelope | About 310 × 224 × 33.3 in head coordinates | R14 geometry, not the earlier 290 mm concept |
| Base plan envelope | 240 × 230 | Assembled CAD footprint; differs from rotated export bounds |
| Tablet opening gauges | 259.03 width / 190.41 height | Nominal +1.00 mm overall relative to body; not a complete fillet/button fit specification |
| USB body gauge Q12 | 16 × 10 × 30 | Provisional reference, not a universal USB-C plug size |
| Stand duct | About 30 wide × 24 central height | Shaped route; local transitions and connector rotation matter |
| Supply reference R02 | 92 × 64.02 × 39.02 | Body envelope only; terminals, access and cooling remain to be verified |
| LED strip width | 8.0 | User-provided width; voltage, package height and bend limit still unspecified |
| LED reserved width | 8.5 | 0.5 total nominal allowance, not 0.5 per side |
| Visible light belt | About 3 | Optical appearance target, not strip width |
| O05 current film | 25.6 × 193.6 × 0.20 | R14.1 single-layer amendment |

## Datums for checking an assembly

Use the desk plane, the base exterior, the head plane and the tablet front glass as distinct references. The provided STL bounding box is measured in its exported print orientation. The native CAD and assembly meshes use assembly coordinates. Do not derive a joint's assembled angle by comparing two rotated STL boxes.

The head display plane is nominally 60° to the desk. The nominal P1S cube is 256 × 256 × 256. A 310 × 224 × 33.3 head rotated edge-on at 45° has an approximate plan projection of (310 + 33.3) / sqrt(2) = 242.75 in both X and Y, with 224 height. Brims, supports, exclusion zones and adhesion space are additional; a bounding-box pass does not establish a usable print job.

## Fit budget

Account separately for extrusion and shrinkage, first-layer expansion, paint thickness, guide clearance and actual component variation. A 1.00 mm total opening allowance gives about 0.50 mm per side only for a centered ideal body in a straight section; corner radii, glass overlap and buttons can govern first contact instead.

Use probe results to decide local adjustments. Do not scale a whole part just to gain a few tenths at one opening: doing so also changes coarse threads, LED seat width and mating datums. Keep optical film thickness changes separate from its outline; the current amendment preserves the film outline and front datum.

## Connector passage

Prove passage with the complete actual connector, not only the flexible cable. Pull the unpowered connector through the stand, head junction and optical-service opening, preserving a safe cable bend. Then add the LED leads and repeat with all required wires present. The path must remain serviceable after covers are installed. A cable should not become the spacer that prevents a structural face from seating.

Record the smallest successful gap and the actual plug model in your build notes. There is no universal “standard body plus reserve” dimension for every molded USB-C plug.

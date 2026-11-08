# Integrated LED Channels, Optical Belts and Internal Wiring

## Dimensions are different functions

| Feature | Nominal design intent |
|---|---|
| Strip PCB width | 8 mm |
| Reserved seating width / reference | 8.5 mm, including 0.5 mm total nominal allowance |
| Visible luminous belt | Approximately 3 mm |
| O05 optical film | 0.20 mm default; unrelated to the tablet display glass |
| Stand cable route | Approximately 30 mm wide × 24 mm central height, with a shaped roof |
| Connector test body | 16 × 10 × 30 mm provisional body, Q12 |

H01 and B01 contain the head/base channel and light-belt geometry. Their integrated shielding/rim geometry is part of those same printed structures. There are no separate L1/L2 black channel pieces to print in the current inventory. A one-material white shell still needs physical testing for light leakage; geometry and opacity are different properties.

## Installation sequence

1. Use Q15 to test the actual LED strip at a complete corner. Check PCB width, component height, adhesive thickness, cut points, bend direction and connector/solder bulk. Do not assume a flat strip can bend edgewise around the rounded perimeter.
2. Feed the strip through the open service side and seat it against the defined perimeter carrier. The reference envelopes R04/R05 show reserved volume; they are not printed strips or proof of insertion feasibility.
3. Position a feed/corner joint where it can be accessed without removing a thread-bearing boss. Insulate solder joints and provide slack for service, without letting wires cross the optical belt.
4. Route head LED and tablet charging leads through B07's explicit internal duct. Route base LED leads within the base's service region, restrained away from the lower-cover screws and rear cartridge.
5. Use the rear conical cable funnel for the real incoming cable; it is a geometric guide, not a certified gland. Confirm strain relief with the actual cable and suitable real electrical components.
6. Close covers temporarily and inspect the belt in a dark room for unwanted emission through seams, vents and large white surfaces. Correct leakage with a compatible validated treatment or design change, not with an assumption based on the render.

## Diffusion and electrical limits

The structural light belt is integrated with the shell; the tiny optical film O05 covers the decorative sensor detail, not the LED belt. White PETG transmission varies by pigment, wall thickness, layer orientation and finish. Compare Q08/Q09/Q10 transmission coupons before selecting brightness. The desired continuous line is a target; uniform corners and invisible cut joints are not established by CAD.

Do not infer strip voltage or power from the 8 mm width. Use the actual manufacturer's strip data. A printed plastic channel is not a conductive heat sink. If the strip requires a dissipating carrier, add a suitable real carrier and reassess the available space. Test the closed assembly at intended brightness and duration with temperature measurements at strip, printed support, power electronics and tablet. No universal safe wattage or charging capability is specified here.

## Ventilation

The head and base include repeated vent patterns and fine concealment features. In slicer preview, confirm that the intended openings remain open and that the thin lattice is actually produced by the nozzle. These features are decorative/dust-obscuring geometry, not an IP-rated dust filter or quantified airflow system. Keep their paths free of infill and wiring; evaluate airflow and temperature with the actual electronics installed.

See the [LED head](../media/renders/07-integrated-head-led-channel.png), [LED base](../media/renders/08-integrated-base-led-channel.png), [root reinforcement](../media/renders/09-stand-root-reinforcement.png) and [cable section](../media/renders/10-internal-cable-duct-section.png) views. Orange LED envelopes are inspection references, not measured light distribution.

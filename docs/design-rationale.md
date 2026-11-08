# Engineering Design Report: A Serviceable Additively Manufactured OnePlus Pad Terminal

## Abstract

VIA investigates the integration of a consumer tablet, a printable mechanical enclosure and an offline interaction demonstrator into a coherent desktop terminal. The principal design problem is architectural: the tablet must appear integrated while remaining removable, its camera and charging connector must remain accessible, and the stand must carry loads without exposing cables or creating a stack of unrelated adapters. The final mechanical publication is based on revision R14, with a later 0.20 mm optical-film amendment designated R14.1 in this repository. The software publication is VIA Terminal / VIA Mobile 1.0.5. This report synthesizes the design decisions and their rationale; it does not claim experimental validation where only CAD or software evidence exists.

## 1. Research question and requirements

The research question is whether an integrated tablet terminal can be manufactured predominantly by fused-filament fabrication while preserving serviceability and a restrained industrial appearance. The requirements were: compatibility with an OPD2203 tablet; white primary structures and near-black secondary details; a continuous S stand; internal charging and lighting routes; integrated head/base light channels; hidden or visually controlled fastening; printable dummy ports; a detailed decorative sensor bar; local user profiles; and a short, understandable offline demonstration. Later requirements prioritized large monoblock structures and printed coarse fasteners over split stand halves, visible adapter blocks and small snap mechanisms.

The constraints conflict. Monoblock geometry reduces visible seams but can increase support requirements. Thin light-transmitting walls preserve material continuity but make optical isolation harder. Printed threads reduce purchased hardware but depend on material, orientation and long-term creep. Fine vent screens can conceal the interior but restrict airflow and may be unresolved by a 0.4 mm nozzle. The design therefore cannot be evaluated by appearance or nominal printer-envelope fit alone.

## 2. Method and evidence classification

The workflow is iterative: requirements → assembly decomposition → nominal tablet envelope → cable and LED keep-out volumes → fastener and service paths → FFF orientation → digital checks → coupons → physical validation. Native R01–R14 revision snapshots preserve the geometric development history. New publication checks inspect the final STL inventory, native solid validity, software builds, protocol tests and rendered meshes.

Four evidence levels are distinguished: (a) requirements and user preferences; (b) geometric implementation visible in CAD; (c) digital checks limited to their stated scope; and (d) physical performance, which is not established by the current publication. CAD collision checks do not establish assembly force, dimensional accuracy or load capacity. A photorealistic render is an illustration of geometry and materials, not a measurement of translucency, stiffness or heat flow.

## 3. System decomposition

The system comprises a tablet head, an integrated stand/power-supply cover and a base/service enclosure. H01 combines the visible front frame, structural rim and integrated LED-channel geometry. H04 and H06 provide lower and upper rear access. H05 is a sliding upper retention bar, locked by pins integrated into H06 rather than by tiny independent pins. B07 combines the constant-width S-shaped load path with the upper power-volume cover; B01 is the base body and B03 its underside access cover. P01 is a separate recessed dummy-port cartridge. O01, O06, O05 and O03 form a serviceable decorative optical assembly with USB access.

This decomposition follows manufacturing and servicing tasks. A component is separated when a material change, a flat print face or service access justifies the interface. It is integrated when separation would create an exposed step, an avoidable alignment problem or an unnecessary small fastener. The result is 30 printed items represented by 17 unique required STL geometries; repeated screws share files and quantities are explicit.

## 4. Tablet integration and human access

The nominal tablet dimensions are taken from the manufacturer [1]. They describe the body, not the active display, corner radius, button protrusions or the exact camera bump. The design uses the original tablet glass as the front interface; no printed transparent sheet covers the active display. The optical film belongs only to the decorative side cassette. The front camera receives a dedicated clearance feature and must remain unobstructed in a physical fit test.

The early head-size proposal of approximately 290 × 220 mm was superseded. The implemented R14 head is approximately 310 × 224 × 33.3 mm in the local head frame, accommodating the side cassette and service geometry. The current dimensions, rather than earlier concept proportions, must be used for printer and desk-space checks.

The tablet-removal strategy is deliberately sequential. USB-C is disconnected through O03; the upper rear screws are released; H06 is withdrawn, removing its integrated locking pins; H05 then slides out along its guides. The tablet can subsequently be supported and lifted through the upper rear opening. This eliminates a concealed snap that appears locked but has no effective stop. Existing CAD service checks report zero tested intersection volume along selected unlocked displacements, but omit real cables, camera protrusions, elastic deformation and manufacturing variation.

## 5. Structural continuity and reinforcement

The S stand is a continuous, constant-width ribbon rather than two mirror halves or a rounded adapter mounted on a separate pedestal. Its lower transition is integrated into the power-volume cover to avoid the visually stepped base criticized during earlier iterations. A real cable void is subtracted from the stand, so the slicer's infill cannot fill that route.

The root reinforcement is intended to support the stand, not the power supply. The R11 lineage incorporated approximately 4 mm diameter X-like braces on the lateral sides of the supply region, while the central reserved envelope remains available for electronics. This placement creates short load paths from the stand root into the surrounding cover walls. Whether the printed layer orientation, perimeter count and these braces provide sufficient stiffness must be established by load testing; no finite-element or creep validation is claimed.

A simple load formulation explains why static appearance is insufficient. The tablet mass reference of 0.552 kg corresponds to approximately 5.42 N under gravity. At an illustrative 0.12 m lever arm, the tablet-only bending moment is about 0.65 N·m. A separate 10 N touch force at a 0.30 m height would contribute 3 N·m; these are illustrative scenarios, not measured design capacities. The stand must also carry its head and accessories. Section stress may be screened using σ = Mc/I, but FFF anisotropy, notches, thread seats and creep make a homogeneous beam calculation inadequate as final verification.

Tipping is assessed separately from stand strength. A necessary static condition is Fh < gΣ(mᵢdᵢ), with dᵢ measured to the relevant tipping edge. Sliding depends on contact material and friction. The final rigid screw feet are not rubber pads, so the earlier TPU cushioning concept cannot be silently assumed. Physical touch and cable-pull tests are required on the actual desk surface.

## 6. Cable routing and electrical integration

The cable path is an explicit curved void inside B07, with a nominal approximately 30 mm-wide and 24 mm-high central passage and a support-conscious roof. A 16 × 10 × 30 mm USB plug reference and Q12 pull-through gauge provide a provisional check. They are not a universal USB-C standard: connector housings, right-angle boots and bend radii vary. The entire connected plug must pass through the route before final assembly.

The side optical cassette contains space for the USB-C plug and cable, not the complete mains charger. Power leads rise through the stand and enter the head internally. LED leads leave their channels near a corner and are routed away from screw seats, the sliding retention bar and the tablet insertion path. A controlled rear funnel belongs to the port cartridge for the real incoming cable. Printed cable geometry is a guide and strain-relief aid; it is not an electrical connector, insulation system or mains certification.

The modeled power supply and USB plug are reference envelopes. Their existence in CAD does not identify a compatible commercial power unit or validate an open-frame mains installation. Supply selection, electrical protection, heat rejection and USB charging protocol must be resolved using the actual components. The enclosure design does not establish OnePlus fast-charging compatibility.

## 7. Lighting architecture

The design separates three dimensions: LED PCB width, internal clearance and visible luminous belt. The final requirement uses an 8 mm strip with nominal 8.5 mm reserved width, leaving 0.5 mm total nominal width allowance. The visible transmission line is approximately 3 mm. The light channel and shielding geometry are integrated into H01 and B01; no separate black channel segment is required for the current print inventory.

Integrated geometry should not be confused with perfect optical isolation. A white PETG part can transmit light through walls outside the intended belt, and a render cannot determine the leakage. The intended arrangement recesses the strip, restricts the visible aperture and uses overlapping structural geometry around service interfaces. Coupon Q15 and the 0.6/0.8/1.0 mm transmission tests help select the real filament and operating brightness. Corners must respect the selected strip's permitted bend direction and minimum radius; the CAD perimeter radius alone does not prove that an ordinary flat strip can follow the route without segmentation.

Thermally, a printed channel is not automatically a heat sink. Strip power per metre, duty cycle, adhesive system and manufacturer requirements determine whether operation against plastic is acceptable or whether an additional conductive carrier is necessary. Test the closed assembly at the intended brightness while measuring strip, support, supply, conversion electronics and tablet temperatures. Optical uniformity and safe temperature must both be demonstrated before long-duration use.

## 8. Printable interfaces and optical cassette

P01 provides depth, tongues and closed dummy cavities so the ports appear integrated rather than as a floating fascia. It is separately printable in black PETG and recessed within the base envelope. The USB-A, USB-C and Ethernet-style features are decorative; they should not be used as electrical interfaces or as sockets for a retained real plug. Fine contact detail is simplified for a 0.4 mm nozzle.

The optical assembly is split for a specific manufacturing reason. O06 has a flat back with its decorative sensor relief facing upward; O01 is an open carrier, avoiding a large unsupported roof above the whole cavity. Solid pedestals support its threaded seats. O05 is captured against an integrated shoulder in H01 and retained by the face/carrier stack, not by a separate miniature frame or tiny loose pin. O03 provides rear USB service access and retention through the existing fasteners. These are mechanical retention intentions that still require a physical dislodgement test.

The current default O05 film is 0.20 mm thick, half of the R14 baseline's 0.40 mm. Its 25.6 × 193.6 mm outline is unchanged. A first layer of 0.20 mm is necessary to obtain a single layer. Natural PETG will generally show extrusion texture and haze; the part is not equivalent to optical glass or a polished camera window. The amendment changes axial stack clearance and should be checked for rattle, edge retention and optical appearance. The thicker alternative remains traceable.

## 9. FFF strategy and finish

The P1S reference volume is nominally 256 mm per axis [2]. A 310 × 224 × 33.3 mm head does not lie flat in that square. Standing on an edge and rotating 45° gives a nominal plan projection (310 + 33.3)/√2 ≈ 242.75 mm and a height of approximately 224 mm. This explains the supplied diagonal orientation; it does not account for a brim, support expansion or excluded bed areas.

The preferred sequence is small coupons before complete parts. Start with Q07 for corner fit, Q11 for camera clearance, Q12 for the connector, Q13/Q14 for overall opening size, thread-clearance coupons and Q15 for the LED corner. Older coupons cannot validate new H05/H06 locking details. The final fit must use the real tablet and connector.

Structural load paths should use substantial perimeters and modeled ribs, with local slicer modifiers around the stand root, head-mount seats and threaded bosses. Infill belongs inside closed structural regions; it must not replace designed voids, fill LED grooves or obstruct ventilation. Suggested starting ranges are 5–6 perimeters, 0.16–0.20 mm structural layers and 15–25% general gyroid infill, with denser local regions selected after coupons. These are trial settings, not a supplied validated profile. Decorative faces may use 0.08–0.12 mm layers, and the film uses one 0.20 mm layer. Vent mesh features require explicit preview inspection because a thin feature can disappear or be overfilled by the slicer.

A satin product appearance normally requires careful surface preparation. Assemble and verify first, then fill/prime/sand and paint only compatible exterior surfaces. Mask optical belts, threads, guides and fit datums. Paint thickness affects joints. Continuous geometry reduces seams, but does not make an FFF surface injection-molded without finishing.

## 10. Offline interaction and failure semantics

VIA Terminal and VIA Mobile execute local landmark processing and persist profiles on the tablet. Named enrollment is followed by face → smile → palm. The profile list is derived reactively from local storage, rather than showing only the currently recognized person. Printed aesthetic sensors do not supply biometric input; the real tablet camera does.

For the phone path, the tablet creates a bounded, signed QR request. Scanning it in VIA Mobile initiates a signed local response over BLE. A stable GATT service avoids a changing service database; a session tag selects the nearby advertising instance, while full session/challenge/request-digest checks remain authoritative. The tablet acknowledges the final transmitted frame only after response verification. A timeout or failed Bluetooth restart is not treated as success. The phone persists the response together with a demo right's use count, allowing retransmission without a second consumption. Android Bluetooth permissions remain necessary [3].

The earlier reverse QR scan was removed to reduce the visitor interaction to a single scan. Earlier unconditional success paths were also removed: selecting QR, showing a request or opening a service must not itself show Paid or Valid. Mobile Back returns to the home screen from confirmation and cancels a pending connection. These are usability and state-management improvements, not payment-system certification.

## 11. Security and validity limits

Hand landmarks describe pose and geometry [4], not an enrolled person's palm-vein identity. The face descriptor is a geometric landmark representation, not a tested biometric embedding with a measured false-accept rate. The demonstration therefore cannot establish that another person's face, hand, photograph or modified client could never be accepted. Likewise, signatures using keys supplied by a peer prove message integrity and key possession, not a trusted financial identity or transit issuer. Demo rights are local and are not protected against a compromised or cloned phone. No real funds are moved.

This limitation is intentional and must remain explicit in an academic account. The contribution is integrated prototyping and clear failure semantics, not an unsupported claim of secure biometric payment authorization.

## 12. Evaluation plan and conclusion

The repository records executable software checks, STL bounding boxes/topology and native CAD validity. Historical service and overhang reports are retained with their original limited scope. The outstanding evaluation comprises: real tablet and connector fit; full service-cycle tests; printed-thread wear and pull-out; stand bending and creep; stability under touch/cable loads; vent printability and airflow; closed-enclosure thermal tests; LED corner uniformity; camera behavior and local profile retention; and BLE interoperability including OFF → ON recovery on the actual tablet and phone.

VIA demonstrates a coherent integration strategy: serviceable top access, a continuous internally routed support, recessed modular decorative interfaces and deliberately separated digital and physical evidence. The current publication is useful as a reproducible engineering prototype and documented design study. It becomes a physically validated product only after the specified tests and component-level decisions are completed.

## References

[1] OnePlus, *OnePlus Pad specifications*: https://www.oneplus.com/ca_en/oneplus-pad/specs

[2] Bambu Lab, *P1-series specifications and print-volume limitations*: https://bambulab.com/en/p1/tech-specs and https://wiki.bambulab.com/en/knowledge-sharing/print-volume-limitations (access may vary by region).

[3] Android Developers, *Bluetooth permissions*: https://developer.android.com/develop/connectivity/bluetooth/bt-permissions

[4] Google AI Edge, *Hand Landmarker*: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker

Project evidence: [CAD provenance](cad-and-validation.md), [printing](printing.md), [verification](verification.md), [software architecture](software.md).

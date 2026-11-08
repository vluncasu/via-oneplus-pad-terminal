# Verification Record — 8 November 2026

## Executed for this publication

- Both latest Android apps compiled from the published source: version 1.0.5, displayed as VIA Terminal / VIA Mobile.
- **19 automated tests passed**, with zero failures/errors across tablet UI, phone Back navigation, local profile persistence, signed QR protocol, BLE frame assembly, session filtering and stale-callback handling.
- Android Lint: zero errors/fatal issues for both apps; warnings remain and are recorded in `verification/android-build.json`.
- Both APK signatures verified; signing certificate matches the previously delivered official 1.0.5 demo builds. No private key is published.
- Neither APK requests INTERNET. ARM64 and the offline model assets are included.
- 32 inventory STL files audited: all closed, consistent winding and within a nominal 256 mm bounding box. Quantity total for required items is 30.
- Native CAD audit records 50 shape objects, plus the explicit O05 0.20 mm amendment. See the actual JSON scopes rather than interpreting every reference/coupon as a printed assembly item.
- New figures render actual supplied component meshes. LED emission and translucency illustrate appearance, not measured optical performance.

## Not established

Physical fit of the actual tablet/USB plug/power module; material strength or creep; safe operating LED power; charging/fast-charge compatibility; optical uniformity; vent/filter performance; print adhesion/support removability; tightening torque; touch/cable-load stability; secure biometric identity; and BLE interoperability or camera accuracy on the actual OnePlus Pad/phone.

Historical R14 CAD service checks and triangle-normal overhang screens are archived evidence with limited scope. They are not physical test certificates. No print-ready G-code or validated multi-plate slicer project is supplied.

Machine-readable evidence: [Android](../verification/android-build.json), [print meshes](../hardware/validation/print-mesh-audit.json), [native CAD](../hardware/validation/native-shape-audit.json), [historical reports](../hardware/validation/r14-baseline).

## Publication and evidence links

The independent [Linux GitHub Actions run](https://github.com/vluncasu/via-oneplus-pad-terminal/actions/runs/42519953773) passed Android compilation, unit tests, Lint and STL checks for the initial publication. The expanded documentation/gallery changes do not revise the Android source or mechanical print geometry.

Use the [requirements matrix](requirements-traceability.md) to see which design requests map to actual parts and which still require physical testing. The [acceptance plan](acceptance-test-plan.md) provides procedures for producing that missing evidence. A test-plan row is not a passed result.

## Expanded documentation edition

The [edition record](../verification/documentation-edition2.json) records 33 captioned renderings, PNG hashes/dimensions and the 28-page handbook with 13 outline entries. All handbook pages were rendered for visual review; local documentation targets and generated catalog consistency were checked. These changes do not alter APKs, CAD geometry or print STLs.

## Direct-edit CAD handoff

The [native/STEP delivery check](../hardware/validation/editable-delivery.json) reopened the clean native file with 30 valid individual solids and round-tripped the complete STEP with 30 valid solids. Assembly bounds agree within recorded numerical precision. The STEP volume differs by approximately 0.0011%, recorded as a translation diagnostic rather than a geometric-equivalence or fit guarantee. Print STL hashes remain unchanged.

# Build and Fit Notes

## Android applications

Both VIA Terminal and VIA Mobile 1.0.5 were compiled from the published source. Nineteen automated tests passed across profile persistence, enrollment state, QR/BLE handling and Mobile Back navigation. Android Lint completed with no errors; warnings remain. The apps do not request INTERNET and bundle the local detection model.

The [GitHub Actions workflow](https://github.com/vluncasu/via-oneplus-pad-terminal/actions/workflows/quality.yml) builds, tests and checks the Android source. Official release APKs preserve the existing demo signing identity; independently built APKs can use another debug key.

## Mechanical files

The clean FreeCAD assembly and complete STEP were reopened with 30 valid individual solids. The supplied print files were checked for closed meshes, consistent face winding and nominal printer bounds. These file checks do not establish physical tablet fit or support-free printing.

The native files contain final editable solids. Reference blocks describe nominal space rather than every purchased component's terminals, connectors or cooling requirements.

## Before a complete build

Use the fit, thread, connector and LED probes first. Check the actual tablet and charging plug, then perform an unpowered dry assembly. Confirm optical-part capture, the top retention bar, rear locking pins, the base cartridge and printed screw engagement.

Follow the [acceptance plan](acceptance-test-plan.md) for physical load, service, charging, lighting and closed-assembly temperature checks. Camera and BLE behavior must be checked on the actual tablet and phone. No structural rating, dust-filter rating, secure biometric identity or payment certification is claimed.

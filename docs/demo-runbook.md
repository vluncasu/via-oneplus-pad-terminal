# Ten-Minute Offline Demo Runbook

This runbook is for VIA Terminal 1.0.5 on the tablet and VIA Mobile 1.0.5 on the phone. It keeps the presentation short while testing real local state transitions. The interface remains Romanian; English instructions below identify the corresponding controls.

## Before the audience arrives

1. Install both official APKs from the [release](https://github.com/vluncasu/via-oneplus-pad-terminal/releases/tag/v1.0.5). Preserve existing local profiles by using a compatible official update rather than uninstalling.
2. Charge both devices. Enable Bluetooth on both, grant Camera and Nearby devices, and confirm that neither permission is blocked by Android settings. Older Android versions may also need location permission/settings for BLE discovery.
3. Choose steady frontal lighting. Keep the real front camera uncovered and clean; the black decorative sensor bar does not perform the recognition.
4. Open VIA Terminal and VIA Mobile. Rehearse one full QR transaction on the actual pair of devices. Internet is unnecessary, but Bluetooth remains necessary for the return confirmation.
5. For a quiet presentation, use the device's Do Not Disturb settings and a dedicated demo account where appropriate. This branch's immersive UI is not a guaranteed Device Owner kiosk or a universal notification blocker.

## Suggested presentation sequence

| Time budget | Demonstration | What the observer should see |
|---|---|---|
| 0–2 minutes | Create a named profile: Profil nou → name → face → smile → palm | One saved profile for one completed enrollment, not a stream of new users |
| 2–3 minutes | Open Experiențe | Every locally saved profile is listed; the count matches actual records |
| 3–6 minutes | Open Plătește and choose the phone/QR route | Tablet displays a request and waits; success does not appear merely from tapping the option |
| 6–8 minutes | Scan tablet QR using VIA Mobile | Phone sends the response locally over BLE; tablet shows the accepted result |
| 8–9 minutes | Repeat with a validation service | Validation follows the scanned request and accepted response, not the service button tap |
| 9–10 minutes | Press Back on Mobile, then show service access / interior figure | Phone returns Home; explain the hidden cable duct and removable upper-rear tablet restraint |

The times are a presentation plan, not a performance measurement. With many participants, keep enrollment and demonstration transactions short; agree who operates the phone and who watches the tablet so cameras are not competing for the same view.

## What each indication establishes

A face/smile/palm indication reflects local detector or landmark logic. It does not certify financial identity, liveness or resistance to impersonation. A signed QR/BLE result establishes that the demo accepted a bounded local protocol response. It does not transfer money or validate an externally issued travel entitlement. Demonstrate the interaction clearly without claiming stronger security than the implementation provides.

## Recover in front of an audience

- **Bluetooth was off:** enable it fully, return to the tablet's Retry state and retry. If the phone has timed out too, retry there as well.
- **QR expired:** generate the new request and scan that one. Do not keep rescanning a screenshot of the old code.
- **Phone is at the result screen:** Back returns Home; start the next operation from there.
- **Recognition is inconsistent:** correct lighting and distance, clear the real front camera and retry one participant at a time. Do not present an unconfirmed state as success.
- **A connection still fails:** use the [troubleshooting guide](troubleshooting.md), rather than repeatedly enrolling duplicate users.

## Session cleanup

Local data survives normal restarts. Decide before the event which demo profiles should remain; do not clear app data in the middle of a session without expecting profile loss. Do not publish participant biometric images, personal names or device backups with the CAD repository. The public build logs and CAD are separate from an audience's local data.

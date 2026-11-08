# VIA Terminal and VIA Mobile — Offline Android Applications

## Release and installation

Download both 1.0.5 APKs from the [release](https://github.com/vluncasu/via-oneplus-pad-terminal/releases/tag/v1.0.5). Displayed names are **VIA Terminal** and **VIA Mobile**. These are demo/debug-signed APKs. Install official updates over existing official demo builds without uninstalling if you need to preserve profiles.

The legacy package IDs `com.via.terminal.claude` and `com.via.mobile.claude` remain intentionally unchanged for upgrade/data continuity. The legacy suffix is not the app's displayed name. Independently compiled debug APKs usually have another signing key and cannot replace an installed APK signed with the publisher's key. No signing key is committed or published.

Minimum Android version is 8.0/API 26; target/compile SDK is 36. ARM64 is included. Real camera and BLE advertising support are needed for the full tablet–phone path. Grant Camera and Nearby devices and enable Bluetooth on both devices. Older Android versions may also require location permission/settings for BLE discovery. The apps do not request INTERNET and do not require an external backend.

## Profile enrollment

Choose New profile / Profil nou, enter the user's name, then complete face → smile → palm. The profile and palm data are saved locally as one DataStore edit. An atomic claim prevents repeated camera frames from creating many users. Experiences / Experiențe lists every stored profile and the true total; it is separate from the currently active recognition result. This data remains on the tablet across normal app restarts. Uninstalling or clearing app data removes local records.

## QR → automatic BLE confirmation

```mermaid
sequenceDiagram
    participant T as VIA Terminal (tablet)
    participant M as VIA Mobile (phone)
    T->>T: Create bounded signed QR request
    M->>T: Scan request displayed on tablet
    M->>M: Verify request, select demo right, persist response
    M->>T: Send signed response in BLE fragments
    T->>T: Verify session, challenge, request hash, signature and demo right
    T-->>M: Final BLE write acknowledged only after acceptance
    T->>T: Display confirmed/valid demo result
    M->>M: Display confirmation; Back returns Home
```

The optical return scan from an earlier iteration is not required. NFC is not implemented. The QR/BLE protocol is a local demonstration, not a payment network. Peer-supplied signing keys prove integrity/key possession, not a trusted financial identity or externally issued entitlement. Demo-right counters are local and cannot resist a compromised phone.

Request lifetime is three minutes. A stable GATT service UUID avoids changing the GATT database; a short advertising tag selects the session, but the full signed protocol checks are authoritative. The receiver bounds fragments and ignores callbacks from invalidated retries. It watches Bluetooth OFF/ON and restarts on a fully enabled adapter; an eight-second startup watchdog replaces indefinite waiting with an actionable error. Mobile limits its connection attempt and can resend a persisted response without consuming a demo right twice.

If an expired tablet session is regenerated, scan the new QR. If the phone has already timed out, press Retry there as well. Bluetooth must be tested on the actual tablet and phone; unit tests do not establish radio interoperability.

## Source modules

| Module | Responsibility |
|---|---|
| app-terminal | Tablet Compose UI, enrollment, profile listing, QR session and result handling |
| app-mobile | Phone scanner, local demo wallet, automatic signed response and Back navigation |
| core-model | Serializable models, signed offline QR protocol and regression tests |
| core-hardware | Optional LED controller plus tablet–phone BLE transport and frame assembly |
| core-vision | Bundled ML Kit face detection, MediaPipe hand landmarks, QR analyzer |
| core-storage | Local DataStore records, atomic person save and demo-response/use persistence |
| core-crypto | Android Keystore keys and signature/encryption helpers |
| core-ui | Shared branding and Compose components |
| core-network | Retained historical network client source; not used by the local runtime |

No cloud model download occurs during runtime. The MediaPipe `.task` asset is included in the release APK. Dependency/model acquisition is a build-time concern.

## Build and test

Install JDK 21, Android SDK platform 36 and the SDK build tools required by the Android Gradle plugin. Set ANDROID_HOME or create an untracked `android/local.properties` containing your SDK path. No absolute developer-machine SDK path is committed.

```bash
cd android
bash ./gradlew :app-terminal:assembleDebug :app-mobile:assembleDebug
bash ./gradlew :app-terminal:testDebugUnitTest :app-mobile:testDebugUnitTest \
  :core-storage:testDebugUnitTest :core-model:testDebugUnitTest :core-hardware:testDebugUnitTest \
  :app-terminal:lintDebug :app-mobile:lintDebug
```

The GitHub workflow runs the same scope and uploads CI APKs as workflow artifacts. CI uses an ephemeral debug key unless signing is configured separately; those artifacts are not guaranteed update-compatible with official demo APKs. Tests use Robolectric/native graphics and pure-JVM protocol logic. They do not replace physical camera, BLE, charging or enclosure tests.

## Kiosk scope

This publication preserves the selected Claude-derived interface and the local fixes. Immersive display/Back behavior is not the same as a configured Android Device Owner kiosk. This branch must not be described as blocking all Android notifications or system exits on every tablet. A dedicated-device deployment needs separately verified Android management configuration.

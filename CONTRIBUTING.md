# Contributing

Keep CAD changes, print exports and English documentation synchronized. Preserve stable part IDs; change the revision and update `hardware/parts.json` hashes when geometry changes. Do not claim support-free printing, secure biometric identification or tested thermal/structural performance without reproducible evidence.

For software changes, run the tests and Lint listed in `docs/software.md`. Do not introduce automatic success when QR/BLE fails. Keep signing keys, profiles, credentials, databases and developer-machine SDK paths out of Git. Changes to legacy package IDs affect update/data continuity and require an explicit migration plan.

For mechanical changes, include CAD provenance, actual STL bounds, affected assembly interfaces, print orientation and physical test status. Keep real assembly meshes separate from printable orientations. Follow third-party terms and the repository rights notice.

For documentation changes, run `python3 scripts/build_part_catalog.py` and `python3 scripts/check_documentation.py` from the repository root. Keep render captions in `media/render-manifest.json` consistent with visibility changes; do not describe a reference envelope as a tested real component. Rebuild the handbook with `python3 scripts/build_handbook.py` after changing its source chapters, then render and visually inspect every PDF page before publishing it.

After intentional image regeneration, run `python3 scripts/check_documentation.py --refresh-render-hashes` to update the recorded PNG hashes and dimensions. Review the changed images and captions before committing the manifest.

# Zed packaging

RPM packaging for [Zed](https://zed.dev/), a third-party code editor,
repackaged for the signed Lyra OS OBS repositories.

- `_service`: OBS source service that fetches and checksum-verifies the
  upstream Linux release tarball and the upstream `LICENSE-GPL` and
  `LICENSE-APACHE` files, all pinned to the same release tag, directly from
  GitHub;
- `zed.spec`: installs the upstream prebuilt binaries with no compilation
  step, strips them, keeps the bundled private libraries out of automatic
  RPM library Provides, validates the desktop file, and fails the build if
  the Zypper-redirect launcher does not set `ZED_UPDATE_EXPLANATION`;
- `zed-launcher`: the `/usr/bin/zed` entry point. It sets
  `ZED_UPDATE_EXPLANATION` so Zed's bundled auto-updater points users at
  Zypper instead of trying to replace a root-owned, RPM-managed install,
  then execs the real binary;
- `zed.changes`: RPM changelog.

This package is not Lyra-authored application code; it is packaging
metadata only. Upstream license and source stay in the tarball fetched by
`_service`.

## Validation

Every push to `main` and pull request runs:

```sh
python3 -m unittest discover -s tests -v
rpmspec -P zed.spec >/dev/null
bash -n zed-launcher
```

The tests require all upstream sources and both licenses to use one pinned
tag, HTTPS and explicit SHA-256 checksums. They also gate the desktop entry,
license installation, bundled-library isolation and Zypper update redirect.

## Credits

Zed is developed by [Zed Industries](https://zed.dev/) and its open-source
contributors. See the [Zed repository](https://github.com/zed-industries/zed)
for the full source and contributor list.

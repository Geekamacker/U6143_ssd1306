# Publish the Raspberry Pi installer through GitHub Releases

This is a maintainer guide for `Geekamacker/U6143_ssd1306`.

## A. Commit the release-ready changes to `master`

Merge/apply the provided modified source files into your GitHub repository.
The `.github/workflows/release.yml` file must exist **in the repository**;
merely attaching a ZIP to a release does not enable GitHub Actions.

If you have a local checkout on a computer, copy the supplied patch file there,
then **review local changes first**:

```bash
cd /path/to/U6143_ssd1306
git status --short
git apply --check /path/to/U6143_ssd1306_release_workflow.patch
git apply /path/to/U6143_ssd1306_release_workflow.patch
git add -A
git commit -m "Add crash diagnostics and GitHub Release installer"
git push origin master
```

If `git apply --check` fails, do **not** force or reset your checkout;
inspect the conflict or compare against the full source ZIP instead.

## B. Publish a versioned release

On GitHub, navigate to **Actions → Publish Raspberry Pi release → Run workflow**.
Choose the `master` branch and enter a new version, such as `v1.0.0`.
The workflow compiles/tests the C source, tests the helpers, packages the
Raspberry Pi files, calculates a checksum, creates the tag (if necessary),
and publishes the assets on GitHub Releases.

Alternatively, pushing a `vX.Y.Z` tag triggers the same workflow.
Avoid manually creating an empty GitHub Release of the same version first.

## C. Install/update on a Pi

Run as the Pi's normal user:

```bash
curl -fsSLo /tmp/uctronics-install-release.sh \
  https://raw.githubusercontent.com/Geekamacker/U6143_ssd1306/master/install_release.sh
bash /tmp/uctronics-install-release.sh
```

The installer downloads the latest non-prerelease release, verifies SHA-256,
installs into a version-specific directory and changes the systemd unit
paths to the new version. The existing Git checkout is not changed.

Pin or roll back to a known version:

```bash
bash /tmp/uctronics-install-release.sh --tag v1.0.0
```

After a reboot, inspect the previous-boot report:

```bash
sudo cat /var/lib/uctronics-display/last_boot_report.txt
```

A hard freeze may leave no logs. The diagnostic page reports clues rather
than presenting an unsupported definitive cause.

## Maintainer notes

- No GitHub release has been published just by creating these local files.
- The workflow requires GitHub Actions and permission to create releases.
- The Raspberry Pi builds the C program locally (arm64/armhf); GitHub only
  performs a Linux compile test.
- Existing local header customizations are not automatically copied into a
  newly installed release.
- Never run `git reset --hard` or delete the existing clone to deploy a release.

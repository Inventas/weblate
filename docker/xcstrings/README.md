<!--
Copyright © Inventas GmbH

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Inventas xcstrings image

This image extends the official Weblate container and installs the Inventas
Weblate fork plus the Inventas translate-toolkit fork with native Apple String
Catalog support.

The stable production tag for the Weblate 2026.5 fork line is:

```text
ghcr.io/inventas/weblate:2026.5-xcstrings
```

The Dockerfile verifies that `translate.storage.xcstrings.XCStringsFile` is
registered and that Weblate exposes the format as a multi-language single-file
format during the image build.

Build locally from the repository root:

```bash
docker build \
  -f docker/xcstrings/Dockerfile \
  -t ghcr.io/inventas/weblate:2026.5-xcstrings \
  .
```

Override `WEBLATE_BASE_IMAGE` only when moving to another upstream Weblate image.
Override `INVENTAS_TRANSLATE_REF` when updating the translate-toolkit fork used
inside the image.

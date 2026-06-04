# Copyright © Inventas GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later

ARG WEBLATE_BASE_IMAGE=weblate/weblate:2026.5
FROM ${WEBLATE_BASE_IMAGE}

ARG INVENTAS_TRANSLATE_REF=8ebe3b624aaaebc5856fea8b2709a6606e2fcc93
ARG INVENTAS_WEBLATE_SOURCE=/usr/src/inventas-weblate

LABEL org.opencontainers.image.source="https://github.com/Inventas/weblate"
LABEL org.opencontainers.image.description="Inventas Weblate with native Apple String Catalog support"

USER root

COPY . ${INVENTAS_WEBLATE_SOURCE}

RUN . /app/venv/bin/activate \
    && uv pip install --no-cache-dir --no-build-isolation --no-deps \
        "https://github.com/Inventas/translate/archive/${INVENTAS_TRANSLATE_REF}.tar.gz" \
    && uv pip install --no-cache-dir --no-build-isolation --no-deps \
        "${INVENTAS_WEBLATE_SOURCE}" \
    && DJANGO_SETTINGS_MODULE=weblate.settings_test python -c "import django; django.setup(); from translate.storage.xcstrings import XCStringsFile; from weblate.formats.ttkit import XCStringsFormat; assert 'xcstrings' in XCStringsFile.Extensions; assert XCStringsFormat.multi_language_file" \
    && rm -rf "${INVENTAS_WEBLATE_SOURCE}"

USER 1000

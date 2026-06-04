# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for multi-language translation files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar
from unittest.mock import patch

from django.core.exceptions import ValidationError

from weblate.formats.base import TranslationFormat, TranslationUnit
from weblate.formats.models import FILE_FORMATS
from weblate.lang.models import Language
from weblate.trans.models import Component, Translation
from weblate.trans.tests.test_models import RepoTestCase
from weblate.utils.state import STATE_EMPTY

if TYPE_CHECKING:
    from weblate.trans.file_format_params import FileFormatParams


@dataclass
class SharedCatalogUnit:
    context: str
    source: str
    target: str


class SharedCatalogStore:
    def __init__(
        self, filename: str, language_code: str | None, catalog: dict
    ) -> None:
        self.filename = filename
        self.language_code = language_code
        self.catalog = catalog
        source_language = catalog.get("sourceLanguage")
        self.units = [
            SharedCatalogUnit(
                context=key,
                source=unit["source"],
                target=unit["source"]
                if language_code == source_language
                else unit.get("localizations", {}).get(language_code, ""),
            )
            for key, unit in catalog.get("strings", {}).items()
        ]

    def save(self) -> None:
        if self.language_code != self.catalog.get("sourceLanguage"):
            for unit in self.units:
                self.catalog["strings"][unit.context].setdefault(
                    "localizations", {}
                )[self.language_code] = unit.target
        Path(self.filename).write_text(
            json.dumps(self.catalog, indent=2, sort_keys=True), encoding="utf-8"
        )


class SharedCatalogTranslationUnit(
    TranslationUnit[SharedCatalogUnit, "SharedCatalogFormat"]
):
    @property
    def source(self) -> str:
        return self.unit.source

    @property
    def target(self) -> str:
        return self.unit.target

    @property
    def context(self) -> str:
        return self.unit.context

    def set_target(self, target: str | list[str]) -> None:
        self._invalidate_target()
        self.unit.target = target[0] if isinstance(target, list) else target

    def set_state(self, state) -> None:
        return

    def untranslate(self, language) -> None:
        self.set_target("")
        self.set_state(STATE_EMPTY)


class SharedCatalogFormat(
    TranslationFormat[
        SharedCatalogStore, SharedCatalogUnit, SharedCatalogTranslationUnit
    ]
):
    name = "Shared test catalog"
    format_id = "test-multilang"
    unit_class = SharedCatalogTranslationUnit
    multi_language_file = True
    monolingual = False
    language_format = "bcp"
    supports_context = True
    autoload: ClassVar[tuple[str, ...]] = ("*.shared.json",)

    def load(self, storefile, template_store):
        filename = str(storefile)
        catalog = json.loads(Path(filename).read_text(encoding="utf-8"))
        return SharedCatalogStore(filename, self.language_code, catalog)

    def add_unit(self, unit: SharedCatalogTranslationUnit) -> None:
        self.store.units.append(unit.unit)

    def save(self) -> None:
        self.store.save()

    @classmethod
    def list_languages(
        cls,
        filename: str,
        file_format_params: FileFormatParams | None = None,  # noqa: ARG003
    ) -> list[str]:
        catalog = json.loads(Path(filename).read_text(encoding="utf-8"))
        source_language = catalog["sourceLanguage"]
        languages = {
            code
            for unit in catalog["strings"].values()
            for code in unit.get("localizations", {})
        }
        return [
            source_language,
            *sorted(code for code in languages if code != source_language),
        ]

    @classmethod
    def is_valid_base_for_new(
        cls,
        base: str,
        monolingual: bool,  # noqa: ARG003
        errors: list[Exception] | None = None,  # noqa: ARG003
        fast: bool = False,  # noqa: ARG003
        file_format_params: FileFormatParams | None = None,  # noqa: ARG003
    ) -> bool:
        return True

    @classmethod
    def create_new_file(
        cls,
        filename: str,
        language: Language,
        base: str,
        callback=None,  # noqa: ARG003
        file_format_params: FileFormatParams | None = None,  # noqa: ARG003
    ) -> None:
        catalog = json.loads(Path(filename).read_text(encoding="utf-8"))
        language_code = cls.get_language_code(language.code)
        for unit in catalog["strings"].values():
            unit.setdefault("localizations", {}).setdefault(language_code, "")
        Path(filename).write_text(
            json.dumps(catalog, indent=2, sort_keys=True), encoding="utf-8"
        )

    def create_unit(
        self,
        key: str,
        source: str | list[str],
        target: str | list[str] | None = None,
    ) -> SharedCatalogUnit:
        if target is None:
            target_value = ""
        elif isinstance(target, list):
            target_value = target[0]
        else:
            target_value = target
        return SharedCatalogUnit(
            context=key,
            source=source[0] if isinstance(source, list) else source,
            target=target_value,
        )


class MultiLanguageFileTest(RepoTestCase):
    catalog_name = "Localizable.shared.json"

    def setUp(self) -> None:
        super().setUp()
        FILE_FORMATS[SharedCatalogFormat.format_id] = SharedCatalogFormat
        field = Component._meta.get_field("file_format")
        old_choices = field.choices
        field.choices = [
            *old_choices,
            (SharedCatalogFormat.format_id, SharedCatalogFormat.name),
        ]
        self.addCleanup(FILE_FORMATS.data.pop, SharedCatalogFormat.format_id, None)
        self.addCleanup(setattr, field, "choices", old_choices)

    def write_catalog(self, component: Component) -> Path:
        filename = Path(component.full_path) / self.catalog_name
        filename.write_text(
            json.dumps(
                {
                    "sourceLanguage": "en",
                    "strings": {
                        "hello": {
                            "source": "Hello",
                            "localizations": {"cs": "Ahoj"},
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        return filename

    def create_shared_component(self) -> Component:
        component = self.create_po()
        self.write_catalog(component)
        component.file_format = SharedCatalogFormat.format_id
        component.filemask = self.catalog_name
        component.new_lang = "add"
        component.save()
        component.refresh_from_db()
        component.drop_file_format_cache()
        return component

    def test_fixed_filemask_validation_requires_multi_language_format(self) -> None:
        component = self.create_po()
        self.write_catalog(component)
        component.filemask = self.catalog_name

        with self.assertRaisesMessage(
            ValidationError, "File mask does not contain * as a language placeholder!"
        ):
            component.full_clean()

        component.file_format = SharedCatalogFormat.format_id
        component.drop_file_format_cache()
        component.full_clean()

    def test_catalog_discovers_languages_with_shared_filename(self) -> None:
        component = self.create_shared_component()

        self.assertEqual([self.catalog_name], component.get_mask_matches())
        self.assertEqual(
            [(self.catalog_name, "en"), (self.catalog_name, "cs")],
            component.get_language_matches(component.get_mask_matches()),
        )
        self.assertEqual(
            {"en": self.catalog_name, "cs": self.catalog_name},
            dict(component.translation_set.values_list("language_code", "filename")),
        )

    def test_uses_changed_files_matches_fixed_catalog_exactly(self) -> None:
        component = self.create_shared_component()

        self.assertTrue(component.uses_changed_files([self.catalog_name]))
        self.assertFalse(component.uses_changed_files([f"prefix-{self.catalog_name}"]))

    def test_add_language_updates_existing_shared_catalog(self) -> None:
        component = self.create_shared_component()
        language = Language.objects.get(code="de")

        with patch.object(Translation, "git_commit", autospec=True, return_value=True):
            translation = component.add_new_language(
                language, None, show_messages=False
            )

        self.assertIsNotNone(translation)
        translation.refresh_from_db()
        self.assertEqual(self.catalog_name, translation.filename)
        catalog = json.loads(
            (Path(component.full_path) / self.catalog_name).read_text(encoding="utf-8")
        )
        self.assertIn("de", catalog["strings"]["hello"]["localizations"])

    def test_shared_file_commit_refreshes_sibling_hashes(self) -> None:
        component = self.create_shared_component()
        source = component.translation_set.get(language_code="en")
        translation = component.translation_set.get(language_code="cs")
        old_source_revision = source.revision

        catalog_file = Path(component.full_path) / self.catalog_name
        catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
        catalog["strings"]["hello"]["localizations"]["cs"] = "Nazdar"
        catalog_file.write_text(json.dumps(catalog), encoding="utf-8")

        with patch.object(Component, "commit_files", return_value=True):
            translation.git_commit(None, "Weblate <noreply@weblate.org>")

        source.refresh_from_db()
        self.assertNotEqual(old_source_revision, source.revision)
        self.assertEqual(source.get_git_blob_hash(), source.revision)

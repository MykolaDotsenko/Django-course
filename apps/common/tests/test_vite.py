from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

from apps.common.templatetags.vite import ViteManifestError, _load_manifest


def render_vite_asset(entry: str = "frontend/src/app.ts") -> str:
    template = Template(f'{{% load vite %}}{{% vite_asset "{entry}" %}}')
    return template.render(Context())


@override_settings(
    VITE_DEV_SERVER_ENABLED=True,
    VITE_DEV_SERVER_ORIGIN="http://127.0.0.1:5173",
)
class ViteDevelopmentAssetTests(SimpleTestCase):
    def test_development_renders_client_before_entry(self) -> None:
        html = render_vite_asset()

        client = '<script type="module" src="http://127.0.0.1:5173/@vite/client"></script>'
        entry = '<script type="module" src="http://127.0.0.1:5173/frontend/src/app.ts"></script>'

        self.assertIn(client, html)
        self.assertIn(entry, html)
        self.assertLess(html.index(client), html.index(entry))

    @override_settings(VITE_DEV_SERVER_ORIGIN="http://localhost:5173/")
    def test_development_normalizes_trailing_origin_slash(self) -> None:
        html = render_vite_asset()

        self.assertIn('src="http://localhost:5173/@vite/client"', html)
        self.assertNotIn("localhost:5173//", html)

    @override_settings(VITE_DEV_SERVER_ORIGIN="http://user:secret@localhost:5173")
    def test_development_rejects_credential_bearing_origin(self) -> None:
        with self.assertRaisesRegex(ViteManifestError, "without credentials"):
            render_vite_asset()

    def test_entry_must_be_canonical_relative_path(self) -> None:
        with self.assertRaisesRegex(ViteManifestError, "canonical relative POSIX path"):
            render_vite_asset("../frontend/src/app.ts")


@override_settings(
    VITE_DEV_SERVER_ENABLED=False,
    STATIC_URL="/static/",
)
class ViteProductionAssetTests(SimpleTestCase):
    def setUp(self) -> None:
        _load_manifest.cache_clear()
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.manifest_path = Path(self.temporary_directory.name) / "manifest.json"

    def tearDown(self) -> None:
        _load_manifest.cache_clear()

    def write_manifest(self, payload: object) -> None:
        self.manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    def render(self) -> str:
        with override_settings(VITE_MANIFEST_PATH=self.manifest_path):
            return render_vite_asset()

    def test_production_renders_entry_css_import_css_script_and_preloads_in_order(self) -> None:
        self.write_manifest(
            {
                "frontend/src/app.ts": {
                    "file": "assets/app-111.js",
                    "src": "frontend/src/app.ts",
                    "isEntry": True,
                    "css": ["assets/app-111.css"],
                    "imports": ["_shared.js", "_feature.js"],
                },
                "_shared.js": {
                    "file": "assets/shared-222.js",
                    "css": ["assets/shared-222.css"],
                    "imports": ["_deep.js"],
                },
                "_deep.js": {
                    "file": "assets/deep-333.js",
                    "css": ["assets/deep-333.css"],
                },
                "_feature.js": {
                    "file": "assets/feature-444.js",
                    "css": ["assets/shared-222.css"],
                },
            }
        )

        html = self.render()

        expected_fragments = (
            '<link rel="stylesheet" href="/static/build/assets/app-111.css">',
            '<link rel="stylesheet" href="/static/build/assets/deep-333.css">',
            '<link rel="stylesheet" href="/static/build/assets/shared-222.css">',
            '<script type="module" src="/static/build/assets/app-111.js"></script>',
            '<link rel="modulepreload" href="/static/build/assets/deep-333.js">',
            '<link rel="modulepreload" href="/static/build/assets/shared-222.js">',
            '<link rel="modulepreload" href="/static/build/assets/feature-444.js">',
        )

        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, html)

        positions = [html.index(fragment) for fragment in expected_fragments]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(html.count("shared-222.css"), 1)

    def test_production_ignores_dynamic_imports_for_initial_preload(self) -> None:
        self.write_manifest(
            {
                "frontend/src/app.ts": {
                    "file": "assets/app.js",
                    "isEntry": True,
                    "dynamicImports": ["charts/rate-chart.ts"],
                },
                "charts/rate-chart.ts": {
                    "file": "assets/rate-chart.js",
                    "isDynamicEntry": True,
                },
            }
        )

        html = self.render()

        self.assertIn("/static/build/assets/app.js", html)
        self.assertNotIn("rate-chart.js", html)

    def test_production_handles_cyclic_import_graph_without_duplicate_preload(self) -> None:
        self.write_manifest(
            {
                "frontend/src/app.ts": {
                    "file": "assets/app.js",
                    "imports": ["_shared.js"],
                },
                "_shared.js": {
                    "file": "assets/shared.js",
                    "imports": ["frontend/src/app.ts"],
                },
            }
        )

        html = self.render()

        self.assertEqual(html.count("shared.js"), 1)
        self.assertEqual(html.count("app.js"), 1)

    def test_missing_manifest_fails_with_actionable_build_instruction(self) -> None:
        with override_settings(VITE_MANIFEST_PATH=self.manifest_path):
            with self.assertRaisesRegex(ViteManifestError, "npm run build"):
                render_vite_asset()

    def test_missing_entry_fails_fast(self) -> None:
        self.write_manifest({"other.ts": {"file": "assets/other.js"}})

        with self.assertRaisesRegex(ViteManifestError, "frontend/src/app.ts"):
            self.render()

    def test_malformed_json_fails_fast(self) -> None:
        self.manifest_path.write_text("{not valid json", encoding="utf-8")

        with self.assertRaisesRegex(ViteManifestError, "unreadable or malformed"):
            self.render()

    def test_malformed_manifest_shapes_fail_fast(self) -> None:
        invalid_payloads: tuple[object, ...] = (
            [],
            {"frontend/src/app.ts": []},
            {"frontend/src/app.ts": {}},
            {"frontend/src/app.ts": {"file": "../escape.js"}},
            {"frontend/src/app.ts": {"file": "assets/app.js", "css": "assets/app.css"}},
            {
                "frontend/src/app.ts": {
                    "file": "assets/app.js",
                    "imports": ["_missing.js"],
                }
            },
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                _load_manifest.cache_clear()
                self.write_manifest(payload)

                with self.assertRaises(ViteManifestError):
                    self.render()

    def test_manifest_is_cached_after_first_production_load(self) -> None:
        self.write_manifest({"frontend/src/app.ts": {"file": "assets/app-first.js"}})

        first = self.render()
        self.write_manifest({"frontend/src/app.ts": {"file": "assets/app-second.js"}})
        second = self.render()

        self.assertIn("app-first.js", first)
        self.assertIn("app-first.js", second)
        self.assertNotIn("app-second.js", second)

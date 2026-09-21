from __future__ import annotations

from datetime import UTC, datetime

from apps.media.models import MediaSourceKind
from apps.media.sources.europeana import parse_europeana_search_payload
from apps.media.sources.wikimedia import parse_wikimedia_search_payload

NOW = datetime(2026, 9, 21, 10, 0, tzinfo=UTC)


def test_wikimedia_payload_normalizes_provenance_without_html():
    payload = {
        "query": {
            "pages": [
                {
                    "pageid": 123,
                    "title": "File:Helsinki tram.jpg",
                    "canonicalurl": "https://commons.wikimedia.org/wiki/File:Helsinki_tram.jpg",
                    "imageinfo": [
                        {
                            "url": "https://upload.wikimedia.org/example.jpg",
                            "mime": "image/jpeg",
                            "width": 1600,
                            "height": 1200,
                            "extmetadata": {
                                "Artist": {"value": "<b>Example Creator</b>"},
                                "Credit": {"value": "Example Archive"},
                                "LicenseShortName": {"value": "CC BY-SA 4.0"},
                                "LicenseUrl": {
                                    "value": "https://creativecommons.org/licenses/by-sa/4.0/"
                                },
                            },
                        }
                    ],
                }
            ]
        }
    }

    candidates = parse_wikimedia_search_payload(payload, retrieved_at=NOW)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.source_kind == MediaSourceKind.WIKIMEDIA_COMMONS
    assert candidate.external_id == "123"
    assert candidate.creator == "Example Creator"
    assert "<b>" not in candidate.attribution_text
    assert candidate.licence_id == "CC BY-SA 4.0"
    assert candidate.width == 1600


def test_wikimedia_skips_non_image_or_non_https_media():
    payload = {
        "query": {
            "pages": [
                {
                    "pageid": 1,
                    "title": "File:bad.svg",
                    "imageinfo": [
                        {
                            "url": "http://example.test/file.svg",
                            "mime": "image/svg+xml",
                        }
                    ],
                }
            ]
        }
    }

    assert parse_wikimedia_search_payload(payload, retrieved_at=NOW) == ()


def test_europeana_preserves_object_rights_for_editorial_review():
    payload = {
        "success": True,
        "items": [
            {
                "id": "/123/example",
                "title": ["Historic Helsinki"],
                "guid": "https://www.europeana.eu/item/123/example",
                "edmIsShownBy": ["https://example.org/media.jpg"],
                "dataProvider": ["Example Museum"],
                "dcCreator": ["A. Creator"],
                "rights": ["https://creativecommons.org/publicdomain/mark/1.0/"],
            }
        ],
    }

    candidates = parse_europeana_search_payload(payload, retrieved_at=NOW)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.source_kind == MediaSourceKind.EUROPEANA
    assert candidate.source_name == "Example Museum"
    assert candidate.rights_statement.startswith("https://")
    assert candidate.retrieved_at == NOW


def test_europeana_candidate_can_retain_unclear_rights_without_becoming_published():
    payload = {
        "success": True,
        "items": [
            {
                "id": "/123/unclear",
                "title": ["Unclear rights"],
                "guid": "https://www.europeana.eu/item/123/unclear",
                "dataProvider": ["Archive"],
            }
        ],
    }

    candidate = parse_europeana_search_payload(payload, retrieved_at=NOW)[0]

    assert candidate.rights_statement == ""
    assert candidate.licence_id == ""

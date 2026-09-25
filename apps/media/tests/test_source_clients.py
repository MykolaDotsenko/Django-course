from __future__ import annotations

import json
from urllib.error import HTTPError

import pytest

from apps.media.sources.base import MediaSourceError
from apps.media.sources.europeana import EuropeanaSearchClient
from apps.media.sources.wikimedia import WikimediaCommonsClient


class FakeResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        status: int = 200,
        url: str = "https://commons.wikimedia.org/w/api.php",
        content_type: str = "application/json",
        content_length: int | None = None,
    ):
        self.payload = payload
        self.status = status
        self.url = url
        self.headers = {"Content-Type": content_type}
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, amount: int) -> bytes:
        return self.payload[:amount]

    def geturl(self) -> str:
        return self.url


def test_wikimedia_client_is_bounded_and_normalizes_transport(monkeypatch):
    payload = json.dumps(
        {
            "query": {
                "pages": [
                    {
                        "pageid": 5,
                        "title": "File:Test.jpg",
                        "canonicalurl": "https://commons.wikimedia.org/wiki/File:Test.jpg",
                        "imageinfo": [
                            {
                                "url": "https://upload.wikimedia.org/test.jpg",
                                "mime": "image/jpeg",
                                "width": 800,
                                "height": 600,
                                "extmetadata": {},
                            }
                        ],
                    }
                ]
            }
        }
    ).encode()
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return FakeResponse(payload)

    monkeypatch.setattr("apps.media.sources.wikimedia.urlopen", fake_urlopen)
    candidates = WikimediaCommonsClient(timeout_seconds=4).search("Helsinki tram", limit=2)

    assert len(candidates) == 1
    assert seen["url"].startswith("https://commons.wikimedia.org/w/api.php?")
    assert "gsrlimit=2" in seen["url"]
    assert seen["timeout"] == 4


def test_wikimedia_media_download_is_bounded_and_validates_final_response(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        return FakeResponse(
            b"jpeg-bytes",
            url="https://upload.wikimedia.org/example/Helsinki.jpg",
            content_type="image/jpeg",
            content_length=10,
        )

    monkeypatch.setattr("apps.media.sources.wikimedia.urlopen", fake_urlopen)

    downloaded = WikimediaCommonsClient(timeout_seconds=4).download_media(
        "https://upload.wikimedia.org/example/Helsinki.jpg"
    )

    assert downloaded.data == b"jpeg-bytes"
    assert downloaded.filename == "Helsinki.jpg"
    assert downloaded.mime_type == "image/jpeg"
    assert seen == {
        "url": "https://upload.wikimedia.org/example/Helsinki.jpg",
        "timeout": 4,
    }


def test_wikimedia_media_download_rejects_untrusted_host_before_network(monkeypatch):
    called = False

    def unexpected_urlopen(request, timeout):
        nonlocal called
        called = True
        raise AssertionError("network should not be called")

    monkeypatch.setattr("apps.media.sources.wikimedia.urlopen", unexpected_urlopen)

    with pytest.raises(MediaSourceError, match="upload.wikimedia.org"):
        WikimediaCommonsClient().download_media("https://evil.example/image.jpg")

    assert called is False


def test_wikimedia_media_download_revalidates_redirect_target(monkeypatch):
    def fake_urlopen(request, timeout):
        return FakeResponse(
            b"jpeg",
            url="https://evil.example/image.jpg",
            content_type="image/jpeg",
        )

    monkeypatch.setattr("apps.media.sources.wikimedia.urlopen", fake_urlopen)

    with pytest.raises(MediaSourceError, match="upload.wikimedia.org"):
        WikimediaCommonsClient().download_media(
            "https://upload.wikimedia.org/example/image.jpg"
        )


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (
            FakeResponse(
                b"html",
                url="https://upload.wikimedia.org/example/image.jpg",
                content_type="text/html",
            ),
            "unsupported content type",
        ),
        (
            FakeResponse(
                b"jpeg",
                url="https://upload.wikimedia.org/example/image.jpg",
                content_type="image/jpeg",
                content_length=11,
            ),
            "byte limit",
        ),
        (
            FakeResponse(
                b"123456",
                url="https://upload.wikimedia.org/example/image.jpg",
                content_type="image/jpeg",
            ),
            "byte limit",
        ),
    ],
)
def test_wikimedia_media_download_rejects_hostile_payloads(monkeypatch, response, message):
    monkeypatch.setattr(
        "apps.media.sources.wikimedia.urlopen",
        lambda request, timeout: response,
    )

    with pytest.raises(MediaSourceError, match=message):
        WikimediaCommonsClient().download_media(
            "https://upload.wikimedia.org/example/image.jpg",
            max_bytes=5,
        )


@pytest.mark.parametrize("query", ["", " " * 3, "x" * 201])
def test_wikimedia_client_rejects_invalid_query_before_network(query):
    with pytest.raises(ValueError):
        WikimediaCommonsClient().search(query)


@pytest.mark.parametrize("limit", [0, 21])
def test_wikimedia_client_rejects_unbounded_limit(limit):
    with pytest.raises(ValueError, match="limit"):
        WikimediaCommonsClient().search("valid", limit=limit)


def test_wikimedia_transport_normalizes_http_error(monkeypatch):
    def fail(request, timeout):
        raise HTTPError(request.full_url, 503, "down", {}, None)

    monkeypatch.setattr("apps.media.sources.wikimedia.urlopen", fail)

    with pytest.raises(MediaSourceError, match="HTTP 503"):
        WikimediaCommonsClient().search("valid")


def test_europeana_client_uses_key_only_in_server_request(monkeypatch):
    payload = json.dumps({"success": True, "items": []}).encode()
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        return FakeResponse(payload)

    monkeypatch.setattr("apps.media.sources.europeana.urlopen", fake_urlopen)

    assert EuropeanaSearchClient(api_key="secret-key").search("Finland", limit=3) == ()
    assert seen["url"].startswith("https://api.europeana.eu/record/v2/search.json?")
    assert "wskey=secret-key" in seen["url"]
    assert "rows=3" in seen["url"]


def test_europeana_authentication_error_is_normalized(monkeypatch):
    def fail(request, timeout):
        raise HTTPError(request.full_url, 401, "unauthorized", {}, None)

    monkeypatch.setattr("apps.media.sources.europeana.urlopen", fail)

    with pytest.raises(MediaSourceError, match="authentication"):
        EuropeanaSearchClient(api_key="bad").search("Finland")


def test_europeana_rate_limit_is_normalized(monkeypatch):
    def fail(request, timeout):
        raise HTTPError(request.full_url, 429, "limited", {}, None)

    monkeypatch.setattr("apps.media.sources.europeana.urlopen", fail)

    with pytest.raises(MediaSourceError, match="rate limit"):
        EuropeanaSearchClient(api_key="key").search("Finland")


@pytest.mark.parametrize("api_key", ["", "   "])
def test_europeana_client_requires_api_key(api_key):
    with pytest.raises(ValueError, match="API key"):
        EuropeanaSearchClient(api_key=api_key)

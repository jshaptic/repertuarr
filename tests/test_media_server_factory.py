"""Unit tests for the media-server client factory / type dispatch."""

import pytest

from bot.jellyfin import JellyfinClient
from bot.media_server import build_media_server_client
from bot.plex import PlexClient


def test_defaults_to_jellyfin_when_type_omitted():
    client = build_media_server_client({"name": "srv", "url": "http://jf.local", "api_key": "k"})
    assert isinstance(client, JellyfinClient)
    assert client.display_name == "Jellyfin"


def test_builds_jellyfin_explicitly():
    client = build_media_server_client({"type": "jellyfin", "url": "http://jf.local", "api_key": "k"})
    assert isinstance(client, JellyfinClient)


def test_builds_plex():
    client = build_media_server_client({"type": "plex", "url": "http://plex.local", "api_key": "tok"})
    assert isinstance(client, PlexClient)
    assert client.display_name == "Plex"


def test_type_is_case_insensitive():
    client = build_media_server_client({"type": "Plex", "url": "http://plex.local", "api_key": "tok"})
    assert isinstance(client, PlexClient)


def test_returns_none_when_unconfigured():
    assert build_media_server_client(None) is None
    assert build_media_server_client({}) is None


def test_returns_none_when_missing_credentials():
    assert build_media_server_client({"type": "plex", "url": "http://plex.local"}) is None
    assert build_media_server_client({"type": "jellyfin", "api_key": "k"}) is None


def test_unknown_type_raises():
    with pytest.raises(ValueError):
        build_media_server_client({"type": "emby", "url": "http://emby.local", "api_key": "k"})

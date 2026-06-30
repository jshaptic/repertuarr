"""
Synchronous Radarr/Sonarr add flow for Telegram carousel requests.

The Arr APIs are accessed through blocking HTTP calls. This module keeps that
work off the asyncio event loop by running inside asyncio.to_thread from the
Telegram callback handler.
"""

import logging
from typing import Optional

import requests

from bot.service_request import make_service_request

logger = logging.getLogger(__name__)


class ArrAddNotFoundError(Exception):
    """Lookup by provider id returned no Arr candidates."""


class ArrAlreadyManagedError(Exception):
    """The requested title is already managed in Arr."""


def arr_service(media_type: str) -> str:
    return 'radarr' if media_type == 'movie' else 'sonarr'


def submit_arr_add(
    db,
    media_type: str,
    id_val: str,
    base_url: str,
    api_key: str,
    quality_profile: Optional[str] = None,
) -> dict:
    """Add a movie or series to Arr and return the created/managed item payload."""
    endpoint = 'movie' if media_type == 'movie' else 'series'
    lookup_endpoint = f"{base_url}/api/v3/{endpoint}/lookup"
    add_endpoint = f"{base_url}/api/v3/{endpoint}"
    service = arr_service(media_type)
    term = f"tmdb:{id_val}" if media_type == 'movie' else f"tvdb:{id_val}"
    headers = {'X-Api-Key': api_key}

    logger.info("Looking up item by ID: %s in %s", term, base_url)
    resp_lookup = make_service_request(
        db,
        service,
        'GET',
        lookup_endpoint,
        headers=headers,
        params={'term': term},
    )
    resp_lookup.raise_for_status()
    results = resp_lookup.json()
    if not results:
        raise ArrAddNotFoundError(term)

    candidate = results[0]
    if candidate.get('id', 0) > 0:
        raise ArrAlreadyManagedError(candidate.get('title') or term)

    rf_resp = make_service_request(
        db,
        service,
        'GET',
        f"{base_url}/api/v3/rootfolder",
        headers=headers,
    )
    root_folders = rf_resp.json()
    if not root_folders:
        raise RuntimeError('No Root Folders configured')

    qp_resp = make_service_request(
        db,
        service,
        'GET',
        f"{base_url}/api/v3/qualityprofile",
        headers=headers,
    )
    profiles = qp_resp.json()
    if not profiles:
        raise RuntimeError('No Quality Profiles configured')

    if quality_profile:
        matched = next(
            (profile for profile in profiles if profile.get('name', '').lower() == quality_profile.lower()),
            None,
        )
        if matched:
            profile_id = matched['id']
            logger.info("Using quality profile '%s' (id=%s)", matched['name'], profile_id)
        else:
            profile_id = profiles[0]['id']
            logger.warning(
                "Quality profile '%s' not found, falling back to '%s'",
                quality_profile,
                profiles[0]['name'],
            )
    else:
        profile_id = profiles[0]['id']
        logger.info("No quality profile specified, using first: '%s'", profiles[0]['name'])

    payload = dict(candidate)
    payload['qualityProfileId'] = profile_id
    payload['rootFolderPath'] = root_folders[0]['path']
    payload['monitored'] = True
    if media_type == 'movie':
        payload['addOptions'] = {'searchForMovie': True}
    else:
        payload['addOptions'] = {'searchForMissingEpisodes': True}
        payload['seasonFolder'] = True

    logger.info("Sending Add Payload for %s", candidate.get('title'))
    added_item = None
    resp_add = None
    try:
        resp_add = make_service_request(
            db,
            service,
            'POST',
            add_endpoint,
            headers=headers,
            json_body=payload,
            timeout=60,
        )
    except requests.exceptions.Timeout as timeout_error:
        logger.warning(
            "Add request timed out for %s; checking whether Arr created it",
            candidate.get('title'),
        )
        recovery_resp = make_service_request(
            db,
            service,
            'GET',
            lookup_endpoint,
            headers=headers,
            params={'term': term},
            timeout=30,
        )
        recovery_resp.raise_for_status()
        for item in recovery_resp.json():
            if item.get('id', 0) > 0:
                added_item = item
                break
        if not added_item:
            raise timeout_error

    if added_item or (resp_add is not None and 200 <= resp_add.status_code < 300):
        logger.info("Add successful.")
        return added_item or resp_add.json()

    raise RuntimeError(f"Add failed: {resp_add.status_code} - {resp_add.text}")

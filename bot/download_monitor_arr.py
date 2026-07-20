"""
Radarr/Sonarr queue and release helpers used by the download monitor.

Keeps HTTP/API details for Arr queue inspection out of the monitor orchestration
loop so that module stays within the project file-size limit.
"""

from typing import Optional

from bot.service_request import make_service_request


def resolve_arr(config: dict, request: dict) -> tuple[str, str]:
    service = request.get('arr_service')
    instance_name = request.get('arr_instance')
    instances = config.get('radarrs' if service == 'radarr' else 'sonarrs', {})
    instance = instances.get(instance_name) if instance_name else None
    if not instance:
        raise ValueError(f"No {service} instance configured for request {request.get('id')}")
    return instance.get('url'), instance.get('key')


def request_headers(api_key: str) -> dict:
    return {'X-Api-Key': api_key}


def queue_records(db, request: dict, base_url: str, api_key: str) -> list:
    response = make_service_request(
        db,
        request['arr_service'],
        'GET',
        f"{base_url}/api/v3/queue",
        headers=request_headers(api_key),
        params={'page': 1, 'pageSize': 250},
    )
    response.raise_for_status()
    payload = response.json()
    records = payload if isinstance(payload, list) else payload.get('records', [])
    arr_id = int(request['arr_id'])

    if request['arr_service'] == 'radarr':
        return [record for record in records if record.get('movieId') == arr_id]
    return [record for record in records if record.get('seriesId') == arr_id]


def first_download_id(records: list) -> Optional[str]:
    for record in records:
        download_id = record.get('downloadId')
        if download_id:
            return str(download_id)
    return None


def queue_block_reason(records: list) -> Optional[str]:
    blocked_states = {'importBlocked', 'importPending'}
    bad_statuses = {'warning', 'error', 'failed'}

    for record in records:
        tracked_state = record.get('trackedDownloadState')
        tracked_status = record.get('trackedDownloadStatus')
        status = record.get('status')
        if tracked_state in blocked_states or tracked_status in bad_statuses or status in bad_statuses:
            messages = []
            error_message = record.get('errorMessage')
            if error_message:
                messages.append(error_message)
            for status_message in record.get('statusMessages') or []:
                title = status_message.get('title')
                if title:
                    messages.append(title)
                messages.extend(status_message.get('messages') or [])
            return "; ".join(messages) or tracked_state or tracked_status or status
    return None


def release_candidates(db, request: dict, base_url: str, api_key: str) -> list:
    params = {'movieId': request['arr_id']}
    if request['arr_service'] == 'sonarr':
        params = {'seriesId': request['arr_id']}

    response = make_service_request(
        db,
        request['arr_service'],
        'GET',
        f"{base_url}/api/v3/release",
        headers=request_headers(api_key),
        params=params,
    )
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else []


def has_acceptable_release(releases: list) -> bool:
    for release in releases:
        if release.get('approved') is True:
            return True
        if 'approved' not in release and not release.get('rejections'):
            return True
    return False

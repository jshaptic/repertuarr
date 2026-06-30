import logging
import json
from aiohttp import web
from .phrases import get_media_type_label, get_phrase
from .phrases import keys as phrase_keys
from .jellyfin import JellyfinClient
from .admin_ui import register_admin_routes
from .webhook_events import build_user_prefs_map, mark_grabbed, notify_failed_requests

logger = logging.getLogger(__name__)

async def start_webhook_server(
    config: dict,
    db,
    jellyfin_client: JellyfinClient,
    bot_app,
    users_config: list,
    messenger_name: str,
):
    """
    Start an aiohttp web server that receives Radarr/Sonarr/Jellyfin webhooks.
    
    Notification strategy:
      - If Jellyfin is configured: Radarr/Sonarr webhooks are ignored for
        notifications (the media isn't in Jellyfin yet). Instead, the Jellyfin
        webhook fires when the item is actually scanned into the library.
      - If Jellyfin is NOT configured: Radarr/Sonarr webhooks notify directly.
    
    Returns the AppRunner (caller is responsible for cleanup).
    """
    port = config.get('webhook_port', 8585)

    user_prefs_map = build_user_prefs_map(users_config, messenger_name)

    # ── Radarr ────────────────────────────────────────────────────────
    
    async def handle_radarr(request: web.Request):
        try:
            payload = await request.json()
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")
        
        event_type = payload.get('eventType', '')
        logger.info(f"Radarr webhook received: {event_type}")
        
        if event_type == 'Test':
            return web.Response(text="OK")

        if event_type == 'MovieAdded':
            movie = payload.get('movie', {})
            logger.info(f"Radarr movie added: '{movie.get('title', '')}'")
            return web.Response(text="OK")
        
        if event_type == 'Grab':
            movie = payload.get('movie', {})
            await mark_grabbed(
                db=db,
                bot_app=bot_app,
                user_prefs_map=user_prefs_map,
                payload=payload,
                title=movie.get('title', ''),
                media_type='movie',
                arr_service='radarr',
                arr_id=movie.get('id'),
                tmdb_id=str(movie.get('tmdbId', '')) if movie.get('tmdbId') else None,
            )
            return web.Response(text="OK")

        if event_type == 'ManualInteractionRequired':
            movie = payload.get('movie', {})
            await notify_failed_requests(
                db=db,
                bot_app=bot_app,
                user_prefs_map=user_prefs_map,
                payload=payload,
                title=movie.get('title', ''),
                media_type='movie',
                arr_service='radarr',
                arr_id=movie.get('id'),
                tmdb_id=str(movie.get('tmdbId', '')) if movie.get('tmdbId') else None,
                reason='manual_interaction_required',
                status='failed',
            )
            return web.Response(text="OK")

        if event_type in ('Health', 'HealthRestored'):
            logger.info(f"Radarr health webhook received: {payload.get('message') or payload.get('health', {})}")
            return web.Response(text="OK")

        if event_type != 'Download':
            return web.Response(text="Ignored")
        
        movie = payload.get('movie', {})
        title = movie.get('title', '')
        tmdb_id = str(movie.get('tmdbId', '')) if movie.get('tmdbId') else None
        
        if not title and not tmdb_id:
            return web.Response(text="No movie data")
        
        logger.info(f"Radarr download: '{title}' (tmdb:{tmdb_id})")
        
        if jellyfin_client:
            logger.info(f"Deferring notification to Jellyfin webhook for '{title}'")
        else:
            await _notify_matching_requests(title, 'movie', tmdb_id=tmdb_id)
        
        return web.Response(text="OK")
    
    # ── Sonarr ────────────────────────────────────────────────────────
    
    async def handle_sonarr(request: web.Request):
        try:
            payload = await request.json()
        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")
        
        event_type = payload.get('eventType', '')
        logger.info(f"Sonarr webhook received: {event_type}")
        
        if event_type == 'Test':
            return web.Response(text="OK")

        if event_type == 'SeriesAdd':
            series = payload.get('series', {})
            logger.info(f"Sonarr series added: '{series.get('title', '')}'")
            return web.Response(text="OK")
        
        if event_type == 'Grab':
            series = payload.get('series', {})
            await mark_grabbed(
                db=db,
                bot_app=bot_app,
                user_prefs_map=user_prefs_map,
                payload=payload,
                title=series.get('title', ''),
                media_type='series',
                arr_service='sonarr',
                arr_id=series.get('id'),
                tvdb_id=str(series.get('tvdbId', '')) if series.get('tvdbId') else None,
            )
            return web.Response(text="OK")

        if event_type == 'ManualInteractionRequired':
            series = payload.get('series', {})
            await notify_failed_requests(
                db=db,
                bot_app=bot_app,
                user_prefs_map=user_prefs_map,
                payload=payload,
                title=series.get('title', ''),
                media_type='series',
                arr_service='sonarr',
                arr_id=series.get('id'),
                tvdb_id=str(series.get('tvdbId', '')) if series.get('tvdbId') else None,
                reason='manual_interaction_required',
                status='failed',
            )
            return web.Response(text="OK")

        if event_type in ('Health', 'HealthRestored'):
            logger.info(f"Sonarr health webhook received: {payload.get('message') or payload.get('health', {})}")
            return web.Response(text="OK")

        if event_type != 'Download':
            return web.Response(text="Ignored")
        
        series = payload.get('series', {})
        title = series.get('title', '')
        tvdb_id = str(series.get('tvdbId', '')) if series.get('tvdbId') else None
        
        if not title and not tvdb_id:
            return web.Response(text="No series data")
        
        logger.info(f"Sonarr download: '{title}' (tvdb:{tvdb_id})")
        
        if jellyfin_client:
            logger.info(f"Deferring notification to Jellyfin webhook for '{title}'")
        else:
            await _notify_matching_requests(title, 'series', tvdb_id=tvdb_id)
        
        return web.Response(text="OK")
    
    # ── Jellyfin ──────────────────────────────────────────────────────
    
    async def handle_jellyfin(request: web.Request):
        # Jellyfin webhook plugin may send text/plain instead of application/json
        body = await request.text()
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            logger.warning(f"Jellyfin webhook: invalid JSON body")
            return web.Response(status=400, text="Invalid JSON")
        
        notification_type = payload.get('NotificationType', '')
        logger.info(f"Jellyfin webhook received: {notification_type}")
        
        if notification_type == 'Test':
            return web.Response(text="OK")
        
        if notification_type != 'ItemAdded':
            return web.Response(text="Ignored")
        
        item_type = payload.get('ItemType', '')
        name = payload.get('Name', '')
        item_id = payload.get('ItemId', '')
        series_name = payload.get('SeriesName', '')
        
        # Map Jellyfin item types to our media types
        if item_type == 'Movie':
            media_type = 'movie'
            title = name
        elif item_type in ('Episode', 'Season', 'Series'):
            media_type = 'series'
            # For episodes, use the series name to match requests
            title = series_name if series_name else name
        else:
            logger.debug(f"Jellyfin ItemAdded ignored for type '{item_type}'")
            return web.Response(text="Ignored")
        
        if not title:
            return web.Response(text="No title")
        
        logger.info(f"Jellyfin item added: '{title}' ({item_type}, id={item_id})")
        
        # Build Jellyfin URL directly from the item ID
        jellyfin_url = None
        if item_id and jellyfin_client:
            jellyfin_url = jellyfin_client.get_item_url(item_id)
        
        await _notify_matching_requests(title, media_type, jellyfin_url=jellyfin_url)
        return web.Response(text="OK")
    
    # ── Shared notification logic ─────────────────────────────────────
    
    async def _notify_matching_requests(
        title: str,
        media_type: str,
        tmdb_id: str = None,
        tvdb_id: str = None,
        jellyfin_url: str = None,
    ):
        """Match a downloaded item against pending requests and notify users."""
        requests_found = db.find_pending_requests(title=title, tmdb_id=tmdb_id, tvdb_id=tvdb_id)
        
        if not requests_found:
            logger.info(f"No pending requests matched for '{title}'")
            return
        
        # If no Jellyfin URL was provided directly, try searching Jellyfin
        if not jellyfin_url and jellyfin_client:
            jellyfin_url = jellyfin_client.search_item(title, media_type)
            logger.info(f"Jellyfin search URL for '{title}': {jellyfin_url}")
        
        for req in requests_found:
            telegram_id = req['telegram_id']
            request_id = req['id']
            prefs = user_prefs_map.get(telegram_id, {'language': 'en', 'bot_style': 'default'})

            req_media_type = req.get('media_type') or media_type
            type_label = get_media_type_label(prefs, req_media_type)
            req_title = req.get('title') or title

            # Build notification text with an inline link (no buttons)
            if jellyfin_url:
                text = get_phrase(
                    prefs,
                    phrase_keys.DOWNLOAD_READY,
                    title=req_title,
                    type=type_label,
                    url=jellyfin_url,
                )
            else:
                text = get_phrase(
                    prefs,
                    phrase_keys.DOWNLOAD_READY_NO_URL,
                    title=req_title,
                    type=type_label,
                )

            try:
                await bot_app.bot.send_message(
                    chat_id=telegram_id,
                    text=text,
                    parse_mode='Markdown',
                )
                db.mark_request_notified(request_id)
                logger.info(f"Notified user {telegram_id} about '{title}'")
            except Exception as e:
                logger.error(f"Failed to notify user {telegram_id} about '{title}': {e}")
    
    # ── Build aiohttp app ─────────────────────────────────────────────
    app = web.Application()
    app.router.add_post('/webhook/radarr', handle_radarr)
    app.router.add_post('/webhook/sonarr', handle_sonarr)
    app.router.add_post('/webhook/jellyfin', handle_jellyfin)
    
    # Register Admin UI and API
    register_admin_routes(
        app,
        db,
        users_config,
        messenger_name,
        recommendation_exclude_ttl_hours=config.get('recommendation_exclude_ttl_hours', 72),
    )
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Webhook server listening on port {port}")
    return runner

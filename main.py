"""
Entrypoint for homelab-bot.

Loads configuration, starts the Telegram bot (polling), HTTP server
(webhooks + admin UI on 8585), and download monitor.

Docker/Unraid env:
  CONFIG_PATH — config file (default: config.yaml; image: /config/config.yaml)
"""

import asyncio
import logging
import os
import yaml
from telegram.ext import ApplicationBuilder
from bot import telegram_bot
from bot.download_monitor import start_download_monitor
from bot.webhook import start_webhook_server
from bot.tmdb import TmdbClient

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "config.yaml"


def _by_name(items: list) -> dict:
    """Index a list of dicts by their 'name' field."""
    return {item['name']: item for item in items}


def _resolve_config_path() -> str:
    """Return config file path from CONFIG_PATH env, else default."""
    return os.environ.get("CONFIG_PATH", DEFAULT_CONFIG_PATH)


async def run_telegram_bot(messenger_conf, bot_config, auth_func):
    """Build and return the Telegram bot application"""
    token = messenger_conf.get('token')
    if not token:
        logger.warning("Telegram token missing in messenger config, skipping bot startup.")
        return None

    # Persistence is intentionally disabled: chat transcript and carousel state
    # now live in the SQLite database (bot/database/chat.py), and per-request
    # state (user_info, session_id) is rebuilt on every update.
    app = (
        ApplicationBuilder()
        .token(token)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .build()
    )
    db, media_server_client = telegram_bot.register_handlers(app, bot_config, auth_func)

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("Started polling for Telegram Bot")

    return app, db, media_server_client


async def main():
    config_path = _resolve_config_path()
    logger.info("Loading config from %s", config_path)
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Config file not found: %s", config_path)
        return

    # Index named sections for quick lookup
    messengers_map  = _by_name(config.get('messengers', []))
    media_servers_map = _by_name(config.get('media_servers', []))
    sonarrs_map     = _by_name(config.get('sonarrs', []))
    radarrs_map     = _by_name(config.get('radarrs', []))

    users_list = config.get('users', [])

    # ── Telegram messenger ─────────────────────────────────────────────
    # Find the first enabled telegram messenger
    telegram_conf = next(
        (m for m in config.get('messengers', [])
         if m.get('type') == 'telegram' and m.get('enabled', False)),
        None
    )

    if not telegram_conf:
        logger.error("No enabled Telegram messenger found in config.")
        return

    messenger_name = telegram_conf['name']

    # Map users whose messenger references this telegram messenger, keyed by telegram user_id
    # Each user has a single messenger: {messenger_name: "<name>", user_id: <id>}
    users_by_telegram_id = {}
    for user in users_list:
        account = user.get('messenger', {})
        if account.get('messenger_name') == messenger_name:
            tg_user_id = account.get('user_id')
            if tg_user_id:
                users_by_telegram_id[tg_user_id] = user

    def check_telegram_auth(user_id):
        """Check if user is authorized via Telegram and return user data, or None."""
        user_data = users_by_telegram_id.get(user_id)
        if not user_data:
            logger.warning(f"Unauthorized Telegram access attempt from {user_id}")
            return None
        return user_data

    # ── Build a flat bot_config dict used by telegram_bot and webhook ──
    # Use the first configured Sonarr / Radarr / Jellyfin for now.
    # (In the future, users could specify which instance they prefer.)
    first_sonarr       = next(iter(sonarrs_map.values()), {})
    first_radarr       = next(iter(radarrs_map.values()), {})
    first_media_server = next(iter(media_servers_map.values()), {})

    bot_section = config.get('bot')
    if not bot_section:
        raise ValueError(f"{config_path} must define a 'bot' section")
    ttl_hours = bot_section.get('recommendation_exclude_ttl_hours')
    if not isinstance(ttl_hours, (int, float)) or ttl_hours <= 0:
        raise ValueError(
            "bot.recommendation_exclude_ttl_hours must be a positive number"
        )
    carousel_count = bot_section.get('recommendation_carousel_count')
    if not isinstance(carousel_count, int) or carousel_count <= 0:
        raise ValueError(
            "bot.recommendation_carousel_count must be a positive integer"
        )
    custom_pool_candidates = bot_section.get('custom_pool_candidates', 50)
    if not isinstance(custom_pool_candidates, int) or custom_pool_candidates <= 0:
        raise ValueError(
            "bot.custom_pool_candidates must be a positive integer"
        )
    inquiry_max_tool_iterations = bot_section.get('inquiry_max_tool_iterations', 4)
    if not isinstance(inquiry_max_tool_iterations, int) or inquiry_max_tool_iterations <= 0:
        raise ValueError(
            "bot.inquiry_max_tool_iterations must be a positive integer"
        )
    add_media_max_titles = bot_section.get('add_media_max_titles', 20)
    if not isinstance(add_media_max_titles, int) or add_media_max_titles <= 0:
        raise ValueError(
            "bot.add_media_max_titles must be a positive integer"
        )

    bot_config = {
        'sonarr_url': first_sonarr.get('url'),
        'sonarr_key': first_sonarr.get('key'),
        'radarr_url': first_radarr.get('url'),
        'radarr_key': first_radarr.get('key'),
        'media_server': first_media_server,
        'recommendation_exclude_ttl_hours': int(ttl_hours),
        'recommendation_carousel_count': carousel_count,
        'custom_pool_candidates': custom_pool_candidates,
        'inquiry_max_tool_iterations': inquiry_max_tool_iterations,
        'add_media_max_titles': add_media_max_titles,
        'download_monitor': bot_section.get('download_monitor', {}),
        'llms': config.get('llms', []),
        'agent': config.get('agent', {}),
        'radarrs': radarrs_map,
        'sonarrs': sonarrs_map,
    }

    # Initialize TMDB Client if configured
    tmdb_config = config.get('tmdb')
    if tmdb_config and tmdb_config.get('bearer_token'):
        tmdb_client = TmdbClient(tmdb_config['bearer_token'])
        tmdb_client.initialize()
        bot_config['tmdb_client'] = tmdb_client
    else:
        logger.warning("No TMDB config or bearer_token found. TMDB discovery will be disabled.")

    app_telegram = None
    http_runner = None
    download_monitor_task = None

    result = await run_telegram_bot(telegram_conf, bot_config, check_telegram_auth)
    if result:
        app_telegram, media_db, media_server_client = result

        # Start webhook + admin UI HTTP server
        http_runner = await start_webhook_server(
            config=bot_config,
            db=media_db,
            media_server_client=media_server_client,
            bot_app=app_telegram,
            users_config=users_list,
            messenger_name=messenger_name,
        )
        download_monitor_task = start_download_monitor(
            config=bot_config,
            db=media_db,
            bot_app=app_telegram,
            users_config=users_list,
            messenger_name=messenger_name,
            media_server_client=media_server_client,
        )

    if not app_telegram:
        logger.error("No bots were started. Check config.")
        return

    # Keep alive
    logger.info("Bot valid and polling. Press Ctrl+C to stop.")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Stopping bot...")
        if download_monitor_task:
            download_monitor_task.cancel()
            try:
                await download_monitor_task
            except asyncio.CancelledError:
                logger.info("Download monitor stopped.")
        if http_runner:
            await http_runner.cleanup()
            logger.info("HTTP server stopped.")
        if app_telegram:
            await app_telegram.updater.stop()
            await app_telegram.stop()
            await app_telegram.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

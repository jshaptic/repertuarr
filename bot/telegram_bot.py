"""
Telegram Bot Handler Module

This module orchestrates the Telegram bot interface. It handles user messages,
processes LLM intent classification (inquiring about media or requesting recommendations),
renders interactive carousels of movies and shows, lazy-loads media metadata,
interacts with Sonarr/Radarr APIs, registers user feedback (watched/disliked),
and manages callback queries for inline button interactions.
"""

import logging
import json
import time
import re
import uuid
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler
from openai import OpenAI
import chevron
import os
from bot.models import IntentResponse, RecommendationResponse
from bot.database import Database
from bot.carousel_feedback_buttons import (
    STYLE_DANGER,
    STYLE_PRIMARY,
    STYLE_SUCCESS,
    feedback_button,
)
from bot.phrases import keys as phrase_keys
from bot.phrases import get_phrase, build_recommend_keyboard, get_jellyfin_play_label, is_recommend_trigger
from bot.phrases.replies import reply_bot_text, send_thinking_message
from bot.jellyfin import JellyfinClient
from bot.session_context import set_session_id, reset_session_id
from bot.service_request import make_service_request
from bot.llm_logging import log_llm_call
from bot.recommendation_prompt import (
    build_feedback_message,
    build_recommendation_input_messages,
    build_system_message,
)
from bot.recommendation_filters import build_candidate_groups_for_request
from bot.filter_planner import run_filter_planner
from bot.inquiry_agent import run_inquiry
from bot.arr_add import ArrAddNotFoundError, ArrAlreadyManagedError, submit_arr_add
from bot.telegram_notify import notify_request_queued
logger = logging.getLogger(__name__)

def load_prompt(prompt_config: dict, **kwargs):
    source = prompt_config.get('source')
    if source != 'local':
        raise ValueError(f"Unsupported prompt source: {source}")
    path = prompt_config.get('path')
    if not path:
        raise ValueError("Prompt path is missing")
    
    if not os.path.isabs(path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(project_root, path)
        
    with open(path, 'r') as f:
        return chevron.render(f, kwargs)

HISTORY_LIMIT = 30

def register_handlers(app: Application, config: dict, auth_func):
    """Registers commands for the Media (*Arr) bot"""
    
    # Initialize OpenAI clients for configured LLMs
    llms = config.get('llms', [])
    agent_config = config.get('agent', {})
    agent_prompts = agent_config.get('prompts', {})
    
    openai_clients = {}
    llm_configs = {}
    for llm in llms:
        name = llm.get('name')
        if not name:
            continue
        llm_configs[name] = llm
        api_key = llm.get('api_key')
        if api_key and llm.get('provider') == 'openai':
            if api_key not in openai_clients:
                openai_clients[api_key] = OpenAI(api_key=api_key)
                
    if not openai_clients:
        logger.warning("OpenAI not configured. LLM features will be disabled.")

    recommendation_exclude_ttl_hours = config['recommendation_exclude_ttl_hours']
    recommendation_exclude_ttl_seconds = recommendation_exclude_ttl_hours * 3600
    recommendation_carousel_count = config['recommendation_carousel_count']
    custom_pool_candidates = config.get('custom_pool_candidates', 50)
    inquiry_max_tool_iterations = config.get('inquiry_max_tool_iterations', 4)

    def get_agent_llm(agent_type: str):
        prompt_cfg = agent_prompts.get(agent_type, {})
        llm_name = prompt_cfg.get('llm')
        cfg = llm_configs.get(llm_name) if llm_name else (llms[0] if llms else {})
        client_instance = openai_clients.get(cfg.get('api_key')) if cfg else None
        return cfg, client_instance

    def build_llm_kwargs(cfg: dict, **base_kwargs):
        kwargs = base_kwargs.copy()
        if 'temperature' in cfg: kwargs['temperature'] = cfg['temperature']
        if 'top_p' in cfg: kwargs['top_p'] = cfg['top_p']
        if 'effort' in cfg: kwargs['reasoning_effort'] = cfg['effort']
        return kwargs
    
    # Initialize database
    db = Database()

    def add_to_history(update: Update, context: ContextTypes.DEFAULT_TYPE, role: str, content: str, sent_message=None):
        """Persist a conversational turn to the DB-backed transcript.

        sent_message, when provided, links the row to its Telegram message id
        (used for user messages so edits can later be synced).
        """
        user = update.effective_user
        chat = update.effective_chat
        if not user or not chat:
            return
        message_id = sent_message.message_id if sent_message is not None else None
        db.add_chat_message(
            user_id=user.id,
            chat_id=chat.id,
            role=role,
            text=content,
            message_id=message_id,
            session_id=context.user_data.get('session_id'),
        )

    def get_llm_history(user_id: int) -> list:
        """Return the recent transcript as OpenAI-style role/content messages."""
        rows = db.get_chat_messages(user_id, limit=HISTORY_LIMIT)
        return [{"role": r["role"], "content": r["text"] or ""} for r in rows]
    
    # Wire database to TMDB client for logging
    tmdb_client = config.get('tmdb_client')
    if tmdb_client:
        tmdb_client.db = db
    
    # Initialize Jellyfin client if configured
    jellyfin_client = None
    jellyfin_url = config.get('jellyfin_url')
    jellyfin_api_key = config.get('jellyfin_api_key')
    if jellyfin_url and jellyfin_api_key:
        jellyfin_client = JellyfinClient(jellyfin_url, jellyfin_api_key)
        jellyfin_client.db = db
        logger.info("Jellyfin client initialized")
    else:
        logger.info("Jellyfin not configured, skipping watch history sync")

    tmdb_client = config.get('tmdb_client')
    if tmdb_client:
        logger.info("TMDB client initialized")
    else:
        logger.info("TMDB not configured, skipping discovery filtering")

    def arr_service(type_: str) -> str:
        return 'radarr' if type_ == 'movie' else 'sonarr'

    def resolve_arr(user_info: dict, media_type: str):
        """Return (url, key) for the user's configured Radarr or Sonarr instance."""
        arr_key = 'radarr' if media_type == 'movie' else 'sonarr'
        arr_map = config.get('radarrs' if media_type == 'movie' else 'sonarrs', {})
        name = user_info.get(arr_key, {}).get('name')
        instance = arr_map.get(name, {})
        return instance.get('url'), instance.get('key')

    def resolve_arr_name(user_info: dict, media_type: str):
        """Return the configured Radarr/Sonarr instance name for a user."""
        arr_key = 'radarr' if media_type == 'movie' else 'sonarr'
        return user_info.get(arr_key, {}).get('name')

    def _user_prefs(context: ContextTypes.DEFAULT_TYPE) -> dict:
        user_info = context.user_data.get('user_info', {})
        return user_info.get('preferences', {})

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = auth_func(update.effective_user.id)
        if not user_data: return
        context.user_data['user_info'] = user_data
        prefs = user_data.get('preferences', {})
        await reply_bot_text(
            update, prefs, phrase_keys.WELCOME,
            add_to_history=add_to_history, context=context,
        )

    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = auth_func(update.effective_user.id)
        if not user_data: return
        context.user_data['user_info'] = user_data
        prefs = user_data.get('preferences', {})
        
        sonarr_url = config.get('sonarr_url')
        sonarr_key = config.get('sonarr_key')
        
        status_lines = []
        
        # Check Sonarr
        if sonarr_url and sonarr_key:
            try:
                resp = make_service_request(
                    db, 'sonarr', 'GET',
                    f"{sonarr_url}/api/v3/system/status",
                    headers={'X-Api-Key': sonarr_key},
                    timeout=5,
                )
                if resp.status_code == 200:
                    status_lines.append(get_phrase(prefs, phrase_keys.STATUS_SONARR_ONLINE))
                else:
                    status_lines.append(get_phrase(
                        prefs, phrase_keys.STATUS_SONARR_ERROR, status_code=resp.status_code,
                    ))
            except Exception as e:
                status_lines.append(get_phrase(
                    prefs, phrase_keys.STATUS_SONARR_UNREACHABLE, error=str(e),
                ))
        else:
            status_lines.append(get_phrase(prefs, phrase_keys.STATUS_SONARR_NOT_CONFIGURED))

        response_text = "\n".join(status_lines)
        keyboard = build_recommend_keyboard(prefs)
        sent = await update.message.reply_text(response_text, reply_markup=keyboard)
        add_to_history(update, context, "assistant", response_text, sent)

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = auth_func(update.effective_user.id)
        if not user_data: return
        context.user_data['user_info'] = user_data
        prefs = user_data.get('preferences', {})
        if not openai_clients:
            await reply_bot_text(
                update, prefs, phrase_keys.LLM_NOT_CONFIGURED,
                add_to_history=add_to_history, context=context,
            )
            return

        user_text = update.message.text
        logger.info(f"Received message: {user_text}")

        session_id = str(uuid.uuid4())
        session_start = time.time()
        detected_intent = None
        session_status = 'completed'

        db.create_session(session_id, update.effective_user.id, user_text)
        context.user_data['session_id'] = session_id
        ctx_token = set_session_id(session_id)

        # Add user message to history
        add_to_history(update, context, "user", user_text, update.message)

        try:
            if is_recommend_trigger(user_text, prefs):
                detected_intent = 'RECOMMEND'
                await handle_recommend_request(
                    update, context, IntentResponse(intent='RECOMMEND', query=None),
                )
                return

            # 1. Classify with LLM
            # Build messages: System + History
            system_content = load_prompt(agent_prompts.get('intent', {}))
            messages = [{"role": "system", "content": system_content}]
            
            # History from DB already includes the user message stored above.
            messages.extend(get_llm_history(update.effective_user.id))
            
            logger.info("Sending LLM Request (Intent)")
            
            start_time = time.time()
            llm_cfg, current_client = get_agent_llm('intent')
            if not current_client:
                raise ValueError("No OpenAI client available for intent classification")
            
            kwargs = build_llm_kwargs(llm_cfg,
                model=llm_cfg.get('model', 'gpt-4o'),
                messages=messages,
                response_format=IntentResponse
            )
            response = current_client.beta.chat.completions.parse(**kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            
            result = response.choices[0].message.parsed
            logger.info(f"LLM Result Parsed: {result}")
            detected_intent = result.intent

            log_llm_call(
                db,
                session_id=session_id,
                user_id=update.effective_user.id,
                user_message=user_text,
                prompt_name='intent',
                kwargs=kwargs,
                response=response,
                parsed=result,
                duration_ms=duration_ms,
                llm_name=llm_cfg.get('name'),
                pricing=llm_cfg.get('pricing'),
            )

            handler = intent_handlers.get(result.intent)
            if handler:
                await handler(update, context, result)
            else:
                await reply_bot_text(
                    update, prefs, phrase_keys.UNKNOWN_INTENT,
                    add_to_history=add_to_history, context=context,
                )

        except Exception as e:
            session_status = 'failed'
            logger.error(f"Error processing message: {e}")
            await reply_bot_text(
                update, prefs, phrase_keys.REQUEST_ERROR,
                add_to_history=add_to_history, context=context,
            )
        finally:
            reset_session_id(ctx_token)
            if context.user_data.get('session_status') == 'failed':
                session_status = 'failed'
            session_duration_ms = int((time.time() - session_start) * 1000)
            db.complete_session(session_id, detected_intent, session_status, session_duration_ms)

    async def handle_inquiry_request(update: Update, context: ContextTypes.DEFAULT_TYPE, data: IntentResponse):
        user_text = update.message.text
        logger.info(f"Handling inquiry for: {user_text}")
        
        prefs = _user_prefs(context)
        user_lang = prefs.get('language', 'en')
        await send_thinking_message(update, prefs, phrase_keys.THINKING_INQUIRY)
        
        try:
            # Build messages: System + History
            system_content = load_prompt(
                agent_prompts.get('inquiry', {}),
                language=user_lang,
                has_tmdb_tools=bool(tmdb_client),
            )
            messages = [{"role": "system", "content": system_content}]

            # Add history from DB
            messages.extend(get_llm_history(update.effective_user.id))

            logger.info(f"Sending LLM Request (Inquiry)")

            llm_cfg, current_client = get_agent_llm('inquiry')
            if not current_client:
                raise ValueError("No OpenAI client available for inquiry")

            parsed = run_inquiry(
                client=current_client,
                llm_cfg=llm_cfg,
                build_llm_kwargs=build_llm_kwargs,
                db=db,
                tmdb_client=tmdb_client,
                messages=messages,
                session_id=context.user_data['session_id'],
                user_id=update.effective_user.id,
                user_text=user_text,
                language=user_lang,
                max_iterations=inquiry_max_tool_iterations,
            )
            if not parsed:
                raise ValueError("Inquiry returned no parsed response")

            reply_text = parsed.reply_text
            keyboard = build_recommend_keyboard(prefs)
            sent = await update.message.reply_text(reply_text, reply_markup=keyboard)
            add_to_history(update, context, "assistant", reply_text, sent)
            
            if parsed.items:
                await start_carousel(update, context, list(parsed.items), 'movie')
                add_to_history(update, context, "assistant", "Shared inquiry results carousel")
            
        except Exception as e:
            context.user_data['session_status'] = 'failed'
            logger.error(f"Inquiry error: {e}")
            await reply_bot_text(
                update, prefs, phrase_keys.INQUIRY_ERROR,
                add_to_history=add_to_history, context=context,
            )

    async def handle_recommend_request(update: Update, context: ContextTypes.DEFAULT_TYPE, data: IntentResponse):
        query = data.query or 'something good'
        logger.info(f"Generating recommendations for: {query}")
        
        prefs = _user_prefs(context)
        user_lang = prefs.get('language', 'en')
        await send_thinking_message(update, prefs, phrase_keys.THINKING_RECOMMEND)
        
        try:
             user_info = context.user_data.get('user_info', {})
             user_name = user_info.get('name', '')
             user_prefs = prefs
             
             # Get preferences for personalized recommendations
             user_preferences = user_prefs.get('profile', '')
             user_guidelines = user_prefs.get('guidelines', '')
             
             # Get watched and disliked content for better recommendations
             user_id = update.effective_user.id
             watched_titles = db.get_feedback_titles(user_id, 'watched')
             disliked_titles = db.get_feedback_titles(user_id, 'disliked')
             
             # Fetch watched content from Jellyfin if configured
             jellyfin_user_id = user_info.get('media_server', {}).get('user_id', '')
             if jellyfin_client and jellyfin_user_id:
                 jellyfin_watched = jellyfin_client.get_watched_items(jellyfin_user_id)
                 # Merge with database watched items (remove duplicates)
                 all_watched = list(set(watched_titles + jellyfin_watched))
                 watched_titles = all_watched
                 logger.info(f"Merged Jellyfin watched items: {len(jellyfin_watched)} from Jellyfin, {len(watched_titles)} total")
             
             # Filter planner: extract concrete constraints for a custom pool.
             # Only runs when the intent produced a query and the planner prompt
             # is configured; the shortcut recommend button never triggers it.
             plan = None
             if tmdb_client and data.query and 'filter_planner' in agent_prompts:
                 try:
                     planner_cfg, planner_client = get_agent_llm('filter_planner')
                     if not planner_client:
                         raise ValueError("No OpenAI client available for filter planner")
                     planner_prompt = load_prompt(
                         agent_prompts.get('filter_planner', {}),
                         movie_genres=sorted(g.title() for g in tmdb_client.movie_genres),
                         tv_genres=sorted(g.title() for g in tmdb_client.tv_genres),
                     )
                     plan = run_filter_planner(
                         client=planner_client,
                         llm_cfg=planner_cfg,
                         build_llm_kwargs=build_llm_kwargs,
                         system_prompt=planner_prompt,
                         query=data.query,
                         history=get_llm_history(user_id)[-6:],
                         db=db,
                         session_id=context.user_data['session_id'],
                         user_id=user_id,
                     )
                 except Exception as plan_e:
                     logger.error(f"Filter planner failed, using predefined sources: {plan_e}")

             # Ask LLM for list with user context
             tmdb_candidate_groups = []
             is_custom_pool = False
             carousel_media_type = 'movie'
             if tmdb_client:
                 recent_tmdb_ids = db.get_recent_excluded_tmdb_ids(
                     user_id, recommendation_exclude_ttl_seconds
                 )
                 recent_titles = db.get_recent_excluded_titles(
                     user_id, recommendation_exclude_ttl_seconds
                 )
                 excluded_tmdb_ids = db.get_excluded_tmdb_ids(user_id) | recent_tmdb_ids
                 excluded_titles = db.get_excluded_titles(user_id) | recent_titles
                 tmdb_candidate_groups, is_custom_pool, pool_media_type = build_candidate_groups_for_request(
                     tmdb_client, plan, user_prefs, user_lang,
                     excluded_tmdb_ids, excluded_titles,
                     recommendation_carousel_count, custom_pool_candidates,
                 )
                 carousel_media_type = 'movie' if pool_media_type == 'movie' else 'series'

             recommendation_prompt = load_prompt(
                 agent_prompts.get('recommend', {}),
                 query=query,
                 language=user_lang,
                 recommendation_count=recommendation_carousel_count,
                 has_tmdb_candidates=bool(tmdb_candidate_groups),
                 tmdb_candidate_groups=tmdb_candidate_groups,
                 is_custom_pool=is_custom_pool,
             )
             system_message = build_system_message(user_name, user_preferences, user_guidelines)
             feedback_message = build_feedback_message(watched_titles[:20], disliked_titles[:20])
             recommendation_input = build_recommendation_input_messages(
                 system_message,
                 feedback_message,
                 recommendation_prompt,
             )
             logger.info("Sending LLM Request (Recommend)")
             
             start_time = time.time()
             llm_cfg, current_client = get_agent_llm('recommend')
             if not current_client:
                 raise ValueError("No OpenAI client available for recommend")
                 
             kwargs = build_llm_kwargs(llm_cfg,
                model=llm_cfg.get('model', 'gpt-4o-mini'),
                input=recommendation_input,
                text_format=RecommendationResponse,
                tools=[{"type": "web_search"}]
             )
             response = current_client.responses.parse(**kwargs)
             duration_ms = int((time.time() - start_time) * 1000)
             parsed_response = response.output_parsed
             logger.info(f"LLM Response Parsed (Recommend): {parsed_response}")

             log_llm_call(
                 db,
                 session_id=context.user_data['session_id'],
                 user_id=update.effective_user.id,
                 user_message=query,
                 prompt_name='recommend',
                 kwargs=kwargs,
                 response=response,
                 parsed=parsed_response,
                 duration_ms=duration_ms,
                 llm_name=llm_cfg.get('name'),
                 pricing=llm_cfg.get('pricing'),
             )

             if not parsed_response or not parsed_response.items:
                 await reply_bot_text(
                     update, prefs, phrase_keys.RECOMMEND_FAILED,
                     add_to_history=add_to_history, context=context,
                 )
                 return

             carousel_items = parsed_response.items[:recommendation_carousel_count]

             await start_carousel(update, context, list(carousel_items), carousel_media_type)
             db.record_recent_recommendations(user_id, carousel_items)
             add_to_history(update, context, "assistant", f"Shared recommendations carousel for '{query}'")

        except Exception as e:
             context.user_data['session_status'] = 'failed'
             logger.error(f"Recommendation error: {e}")
             await reply_bot_text(
                 update, prefs, phrase_keys.RECOMMEND_ERROR,
                 add_to_history=add_to_history, context=context,
             )

    async def handle_add_media_request(update: Update, context: ContextTypes.DEFAULT_TYPE, data: IntentResponse):
        title = data.title
        media_type = data.media_type # Default to movie
        prefs = _user_prefs(context)
        
        if not title:
            await reply_bot_text(
                update, prefs, phrase_keys.ADD_MEDIA_NO_TITLE,
                add_to_history=add_to_history, context=context,
            )
            return

        await send_thinking_message(update, prefs, phrase_keys.THINKING_ADD_MEDIA)

        logger.info(f"Initiating search for '{title}' as {media_type}")

        user_info = context.user_data.get('user_info', {})

        if media_type == 'movie':
            url, key = resolve_arr(user_info, 'movie')
            if not url:
                await reply_bot_text(update, prefs, phrase_keys.NO_RADARR)
                return
            await search_and_display(update, context, title, url, key, 'movie')

        elif media_type == 'series':
            url, key = resolve_arr(user_info, 'series')
            if not url:
                await reply_bot_text(update, prefs, phrase_keys.NO_SONARR)
                return
            await search_and_display(update, context, title, url, key, 'series')
        else:
             await reply_bot_text(
                 update, prefs, phrase_keys.AMBIGUOUS_MEDIA_TYPE, title=title,
                 add_to_history=add_to_history, context=context,
             )

    async def search_and_display(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, base_url: str, api_key: str, type_: str):
        prefs = _user_prefs(context)
        type_label = type_.capitalize()
        endpoint = "movie" if type_ == "movie" else "series"
        lookup_endpoint = f"{base_url}/api/v3/{endpoint}/lookup"
        
        try:
            logger.info(f"Searching API: {lookup_endpoint} term={title}")
            params = {'term': title}
            resp = make_service_request(
                db, arr_service(type_), 'GET', lookup_endpoint,
                headers={'X-Api-Key': api_key}, params=params,
            )
            resp.raise_for_status()
            results = resp.json()
            
            if not results:
                logger.info("Search returned 0 results.")
                await reply_bot_text(
                    update, prefs, phrase_keys.NO_SEARCH_RESULTS,
                    title=title, type=type_label,
                    add_to_history=add_to_history, context=context,
                )
                return
            
            # --- Filtering & Sorting ---
            filtered_results = []
            for item in results:
                status = item.get('status', '').lower()
                if status in ['announced', 'upcoming', 'tba']:
                    continue
                filtered_results.append(item)
            
            if not filtered_results:
                 await reply_bot_text(
                     update, prefs, phrase_keys.NO_RELEASED_MEDIA, title=title,
                     add_to_history=add_to_history, context=context, parse_mode='Markdown',
                 )
                 return

            # Sort by Popularity
            filtered_results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            
            # Take top 5
            candidates = filtered_results[:5]
            
            # Send first card and persist its state keyed by the message id
            await start_carousel(update, context, candidates, type_)
            add_to_history(update, context, "assistant", f"Shared search results carousel for '{title}'")

        except Exception as e:
            logger.error(f"Search Exception: {e}")
            await reply_bot_text(
                update, prefs, phrase_keys.ARR_ERROR, type=type_label,
                add_to_history=add_to_history, context=context,
            )

    async def lookup_metadata(title: str, year: int, type_: str, user_info: dict):
        # Helper to find specific item in Radarr/Sonarr to get ID and Poster
        base_url, api_key = resolve_arr(user_info, type_)
        if not base_url:
            return None
        endpoint = "movie" if type_ == "movie" else "series"
        
        try:
            # We search slightly strictly? Or just use lookup and match logic?
            # Lookup is best.
            url = f"{base_url}/api/v3/{endpoint}/lookup"
            resp = make_service_request(
                db, arr_service(type_), 'GET', url,
                headers={'X-Api-Key': api_key}, params={'term': title},
            )
            
            if resp.status_code == 200:
                results = resp.json()
                # Find best match by year
                for item in results:
                    # Fuzzy match year if possible, or just take first popular match?
                    # API returns sorted list usually. checking year is safer.
                    if item.get('year') == year:
                        return item
                    # If year is missing in our generated data, stick to first result?
                    # Or if off by 1 year.
                    if abs(item.get('year', 0) - year) <= 1:
                        return item
                
                if results: return results[0] # Fallback to first
        except Exception as e:
            logger.error(f"Metadata lookup failed: {e}")
        return None

    def make_safe_callback_data(action: str, type_: str, id_val: str, title: str) -> str:
        """
        Creates a callback_data string for Telegram inline keyboard button.
        Ensures that the total UTF-8 byte length is strictly less than 64 bytes by truncating the title if needed.
        """
        prefix = f"{action}|{type_}|{id_val}|"
        prefix_bytes_len = len(prefix.encode('utf-8'))
        # Telegram limit is 64 bytes. Let's cap at 60 bytes to be safe.
        max_title_bytes = 60 - prefix_bytes_len
        
        title_bytes = title.encode('utf-8')
        if len(title_bytes) > max_title_bytes:
            truncated_title = title_bytes[:max_title_bytes].decode('utf-8', errors='ignore')
            title = truncated_title.strip()
            
        return f"{prefix}{title}"

    async def send_carousel_card(update: Update, context: ContextTypes.DEFAULT_TYPE, results: list, idx: int, type_: str, is_new: bool = False):
        """Render the card at results[idx]. Mutates results in place on lazy
        metadata loads; the caller is responsible for persisting carousel state.
        Returns the sent/edited Telegram Message (or None)."""
        if not results or idx < 0 or idx >= len(results):
            return None

        item = results[idx]
        total = len(results)
        
        # LAZY LOADING METADATA
        # Check if we have an ID (Radarr/Sonarr ID or TMDB/TVDB ID). 
        # Generated items might be Pydantic models or dicts from API.
        # Use getattr for Pydantic, dict.get for dicts
        lookup_title = None  # Will be set to original_title where available
        if isinstance(item, dict):
            id_val = item.get('tmdbId') if type_ == 'movie' else item.get('tvdbId')
            t = item.get('title', 'N/A')
            y = item.get('year', 'N/A')
            overview = item.get('overview', 'No description available')
            lookup_title = item.get('original_title')  # Use original title for Radarr/Sonarr search
        else:
            # Pydantic model from recommendations
            id_val = getattr(item, 'tmdb_id', None) if type_ == 'movie' else None
            t = item.title
            y = item.year
            overview = item.overview
            lookup_title = getattr(item, 'original_title', t)  # Use original title for Radarr/Sonarr search
        if not id_val:
            # Need to lookup — use original_title for API search if available
            search_title = lookup_title or t
            logger.info(f"Lazy loading metadata for '{t}' (searching as '{search_title}')")
            full_item = await lookup_metadata(search_title, y if isinstance(y, int) else 0, type_, context.user_data.get('user_info', {}))
            
            if full_item:
                # Preserve localized display fields from LLM
                full_item['_display_title'] = t
                full_item['_display_overview'] = overview
                results[idx] = full_item
                item = full_item
            else:
                # Item not found in DB
                # If it was a Pydantic model, convert to dict to add 'overview'
                if not isinstance(item, dict):
                    item = item.model_dump() # Convert Pydantic to dict
                    results[idx] = item # Update in results
                item['overview'] = item.get('overview', '❌ Not found in database.')
        
        # Now item is a dict (either from API or lazy-loaded) or a Pydantic model (if lookup failed and it started as one)
        # Extract display fields
        if isinstance(item, dict):
            id_val = item.get('tmdbId') if type_ == 'movie' else item.get('tvdbId')
            t = item.get('_display_title', item.get('title', 'N/A'))
            y = item.get('year', 'N/A')
            overview = item.get('_display_overview', item.get('overview', 'No description available'))
            remote_poster = item.get('remotePoster')
            if not remote_poster and item.get('images'):
                for img in item.get('images'):
                    if img.get('coverType') == 'poster':
                        remote_poster = img.get('url')
                        break
        else: # Pydantic model
            id_val = None # Pydantic models from LLM don't have these IDs initially
            t = item.title
            y = item.year
            overview = item.overview
            remote_poster = None # Pydantic models from LLM don't have remotePoster or images

        if not remote_poster:
            remote_poster = "https://placehold.co/600x900/png?text=No+Poster"
        
        if overview and len(overview) > 150: overview = overview[:147] + "..."
        
        prefs = _user_prefs(context)
        footer = get_phrase(prefs, phrase_keys.CAROUSEL_FOOTER, idx=idx + 1, total=total)
        caption = f"🎬 **{t}** ({y})\n{overview}\n\n{footer}"
        
        # Buttons:
        # Row 1: feedback toggles
        # Row 2: add/download state
        # Row 3: carousel navigation
        if isinstance(item, dict):
            id_val = item.get('tmdbId') if type_ == 'movie' else item.get('tvdbId')
        else:
            id_val = getattr(item, 'tmdb_id', None) if type_ == 'movie' else None

        # Check if item is already available
        jf_url = None
        already_available = False
        if id_val:
            # Check Jellyfin first — use provider ID for precise matching
            if jellyfin_client:
                tmdb_id = str(id_val) if type_ == 'movie' else None
                tvdb_id = str(id_val) if type_ == 'series' else None
                jf_url = jellyfin_client.search_item(t, type_, tmdb_id=tmdb_id, tvdb_id=tvdb_id)
                if jf_url:
                    already_available = True
            # Fallback: check if already managed by Radarr/Sonarr (id > 0)
            arr_id = item.get('id', 0) if isinstance(item, dict) else 0
            if not already_available and arr_id > 0:
                already_available = True
        
        feedback_content_id = db.normalize_content_id(type_, str(id_val or "0"), t)
        feedback_state = {'watched': False, 'feedback': None, 'excluded': False}
        if update.effective_user:
            feedback_state = db.get_content_feedback_state(update.effective_user.id, feedback_content_id)

        watched = bool(feedback_state.get('watched'))
        feedback = feedback_state.get('feedback')
        excluded = bool(feedback_state.get('excluded'))

        # First row: feedback actions
        ignore_data = make_safe_callback_data("IGNORE", type_, str(id_val or "0"), t)
        watched_data = make_safe_callback_data("WATCHED", type_, str(id_val or "0"), t)
        disliked_data = make_safe_callback_data("DISLIKED", type_, str(id_val or "0"), t)
        liked_data = make_safe_callback_data("LIKED", type_, str(id_val or "0"), t)

        rows = [[
            feedback_button("🙈", ignore_data, selected=excluded, selected_style=STYLE_PRIMARY),
            feedback_button("👁️", watched_data, selected=watched and feedback is None, selected_style=STYLE_PRIMARY),
            feedback_button("👁️👎", disliked_data, selected=watched and feedback == "dislike", selected_style=STYLE_DANGER),
            feedback_button("👁️👍", liked_data, selected=watched and feedback == "like", selected_style=STYLE_SUCCESS),
        ]]

        # Second row: Add button only
        if id_val:
            add_label = get_phrase(prefs, phrase_keys.INLINE_ADDED) if already_available else get_phrase(prefs, phrase_keys.INLINE_ADD)
            add_button = InlineKeyboardButton(add_label, callback_data="NOP" if already_available else f"ADD|{type_}|{id_val}")
            rows.append([add_button])
            
        # Third row: Navigation
        nav_row = []
        if idx > 0:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data="NAV|PREV"))
        else:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data="NOP"))  # Disabled
        
        if idx < total - 1:
            nav_row.append(InlineKeyboardButton("➡️", callback_data="NAV|NEXT"))
        else:
            nav_row.append(InlineKeyboardButton("➡️", callback_data="NOP"))  # Disabled
            
        rows.append(nav_row)

        if jf_url:
            play_label = get_jellyfin_play_label(prefs)
            rows.append([InlineKeyboardButton(play_label, url=jf_url)])
            
        inline_markup = InlineKeyboardMarkup(rows)
        
        try:
            from telegram import InputMediaPhoto
            msg = update.callback_query.message if not is_new else None
            
            if is_new:
                if remote_poster:
                     return await update.message.reply_photo(
                         photo=remote_poster,
                         caption=caption,
                         parse_mode='Markdown',
                         reply_markup=inline_markup,
                     )
                else:
                     return await update.message.reply_text(
                         text=caption,
                         parse_mode='Markdown',
                         reply_markup=inline_markup,
                     )
            elif msg: 
                 if remote_poster:
                      if msg.photo:
                          await msg.edit_media(media=InputMediaPhoto(media=remote_poster, caption=caption, parse_mode='Markdown'), reply_markup=inline_markup)
                      else:
                          await msg.edit_text(text=caption, parse_mode='Markdown', reply_markup=inline_markup)
                 else:
                      if msg.photo:
                           await msg.edit_caption(caption=caption, parse_mode='Markdown', reply_markup=inline_markup)
                      else:
                           await msg.edit_text(text=caption, parse_mode='Markdown', reply_markup=inline_markup)
                 return msg

        except Exception as ex:
            logger.error(f"Error sending/editing card: {ex}")
        return None

    async def start_carousel(update: Update, context: ContextTypes.DEFAULT_TYPE, items: list, type_: str):
        """Send a fresh carousel card and persist its state keyed by message id."""
        sent = await send_carousel_card(update, context, items, 0, type_, is_new=True)
        if sent:
            db.save_carousel_state(
                chat_id=sent.chat_id,
                message_id=sent.message_id,
                user_id=update.effective_user.id,
                media_type=type_,
                results=items,
                index=0,
                session_id=context.user_data.get('session_id'),
            )
        return sent

    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        
        user_data = auth_func(update.effective_user.id)
        if not user_data: 
            await query.answer(get_phrase(_user_prefs(context), phrase_keys.UNAUTHORIZED), show_alert=True)
            return
        context.user_data['user_info'] = user_data
        prefs = _user_prefs(context)

        data = query.data
        logger.info(f"Callback received: {data}")

        if data.startswith("NAV|"):
            direction = data.split("|")[1]
            chat_id = query.message.chat_id
            message_id = query.message.message_id

            state = db.get_carousel_state(chat_id, message_id)
            if not state:
                await query.answer(get_phrase(prefs, phrase_keys.CAROUSEL_EXPIRED), show_alert=True)
                return

            results = state['results']
            type_ = state['media_type']
            idx = state['idx']
            total = len(results)

            if direction == "NEXT":
                idx = min(total - 1, idx + 1)
            elif direction == "PREV":
                idx = max(0, idx - 1)

            await send_carousel_card(update, context, results, idx, type_, is_new=False)
            # Persist mutated results (lazy-loaded metadata) and the new index
            db.save_carousel_state(
                chat_id=chat_id,
                message_id=message_id,
                user_id=update.effective_user.id,
                media_type=type_,
                results=results,
                index=idx,
                session_id=state.get('session_id'),
            )
            await query.answer()
            return
        
        feedback_actions = ("WATCHED|", "DISLIKED|", "DISLIKE|", "LIKED|", "IGNORE|")
        if data.startswith(feedback_actions):
            # Format: ACTION|type|id|title
            parts = data.split("|", 3)
            raw_action = parts[0].lower()
            content_type = parts[1]
            content_id = parts[2]
            title = parts[3] if len(parts) > 3 else "Unknown"

            # Try to recover full non-truncated title from message caption or text
            msg = update.callback_query.message
            if msg:
                text = msg.caption or msg.text or ""
                if text:
                    first_line = text.split("\n")[0].strip()
                    first_line = first_line.lstrip("🎬").strip()
                    # Strip trailing "(Year)" or "(N/A)"
                    recovered_title = re.sub(r"\s*\((?:\d{4}|N/A)\)$", "", first_line)
                    if recovered_title:
                        title = recovered_title
            
            user_id = update.effective_user.id
            feedback_action = {
                "watched": "watched",
                "disliked": "dislike",
                "dislike": "dislike",
                "liked": "like",
                "ignore": "ignore",
            }[raw_action]
            content_key = db.normalize_content_id(content_type, content_id, title)
            
            # Extract TMDB/TVDB IDs from callback data
            tmdb_id = content_id if content_type == "movie" and content_id != "0" else None
            tvdb_id = content_id if content_type == "series" and content_id != "0" else None

            db.toggle_feedback_state(
                user_id=user_id,
                content_id=content_key,
                content_type=content_type,
                title=title,
                action=feedback_action,
                tmdb_id=tmdb_id,
                tvdb_id=tvdb_id,
            )
            
            if feedback_action in ("watched", "like"):
                feedback_msg = get_phrase(prefs, phrase_keys.FEEDBACK_WATCHED)
            elif feedback_action == "dislike":
                feedback_msg = get_phrase(prefs, phrase_keys.FEEDBACK_DISLIKED)
            else:
                feedback_msg = get_phrase(prefs, phrase_keys.FEEDBACK_IGNORED)

            await query.answer(feedback_msg, show_alert=False)

            chat_id = query.message.chat_id
            message_id = query.message.message_id
            state = db.get_carousel_state(chat_id, message_id)
            if state:
                results = state['results']
                type_ = state['media_type']
                idx = state['idx']
                total = len(results)
                next_idx = min(total - 1, idx + 1)

                await send_carousel_card(update, context, results, next_idx, type_, is_new=False)
                db.save_carousel_state(
                    chat_id=chat_id,
                    message_id=message_id,
                    user_id=user_id,
                    media_type=type_,
                    results=results,
                    index=next_idx,
                    session_id=state.get('session_id'),
                )

            logger.info(f"User {user_id} toggled {feedback_action} for {title}")
            return

        if not data.startswith("ADD|"): 
            await query.answer()
            return

        await query.answer(get_phrase(prefs, phrase_keys.ADDING_TO_LIBRARY)) 
        
        _, type_, id_val = data.split("|")
        
        user_id = update.effective_user.id
        user_info = context.user_data.get('user_info', {})
        if type_ == 'movie':
             url, key = resolve_arr(user_info, 'movie')
             if not url:
                 await query.answer(get_phrase(prefs, phrase_keys.NO_RADARR), show_alert=True)
                 return
             quality_profile = user_info.get('radarr', {}).get('quality_profile')
             arr_instance = resolve_arr_name(user_info, 'movie')
             await perform_add(query, id_val, url, key, 'movie', user_id, quality_profile, prefs, arr_instance)
        else:
             url, key = resolve_arr(user_info, 'series')
             if not url:
                 await query.answer(get_phrase(prefs, phrase_keys.NO_SONARR), show_alert=True)
                 return
             quality_profile = user_info.get('sonarr', {}).get('quality_profile')
             arr_instance = resolve_arr_name(user_info, 'series')
             await perform_add(query, id_val, url, key, 'series', user_id, quality_profile, prefs, arr_instance)

    async def perform_add(query, id_val: str, base_url: str, api_key: str, type_: str, user_id: int = None, quality_profile: str = None, prefs: dict = None, arr_instance: str = None):
        try:
            added_item = await asyncio.to_thread(
                submit_arr_add,
                db,
                type_,
                id_val,
                base_url,
                api_key,
                quality_profile,
            )
        except ArrAddNotFoundError:
            add_not_found = get_phrase(prefs or {}, phrase_keys.ADD_NOT_FOUND)
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n{add_not_found}",
                parse_mode='Markdown',
            )
            return
        except ArrAlreadyManagedError as already_managed:
            already_in_library = get_phrase(prefs or {}, phrase_keys.ALREADY_IN_LIBRARY)
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n{already_in_library}",
                parse_mode='Markdown',
            )
            logger.info("Item %s already exists.", already_managed)
            return
        except Exception as e:
            logger.error(f"Exception during perform_add: {e}")
            try:
                add_error = get_phrase(prefs or {}, phrase_keys.ADD_ERROR)
                if query.message.caption:
                    await query.edit_message_caption(
                        caption=f"{query.message.caption}\n\n{add_error}",
                        parse_mode='Markdown',
                    )
                else:
                    await query.edit_message_text(
                        text=f"{query.message.text}\n\n{add_error}",
                        parse_mode='Markdown',
                    )
            except Exception:
                pass
            return

        title = added_item.get('title') or 'requested item'
        request_id = None
        if user_id:
            tmdb_id = str(added_item.get('tmdbId') or '') if type_ == 'movie' else None
            tvdb_id = str(added_item.get('tvdbId') or '') if type_ == 'series' else None
            request_id = db.add_media_request(
                telegram_id=user_id,
                title=title,
                media_type=type_,
                tmdb_id=tmdb_id,
                tvdb_id=tvdb_id,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                arr_service=arr_service(type_),
                arr_instance=arr_instance,
                arr_id=added_item.get('id'),
            )

        if request_id:
            await notify_request_queued(
                db,
                query.get_bot(),
                request_id,
                user_id,
                prefs or {},
                title,
            )


    async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wipe the user's stored chat transcript and carousel state."""
        user_data = auth_func(update.effective_user.id)
        if not user_data:
            return
        context.user_data['user_info'] = user_data
        removed = db.clear_chat(update.effective_user.id)
        db.clear_user_carousels(update.effective_user.id)
        db.clear_recent_recommendations(update.effective_user.id)
        prefs = user_data.get('preferences', {})
        text = get_phrase(prefs, phrase_keys.CLEAR_CHAT, removed=removed)
        keyboard = build_recommend_keyboard(prefs)
        await update.message.reply_text(text, reply_markup=keyboard)

    async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Keep the stored transcript in sync when a user edits a message."""
        user_data = auth_func(update.effective_user.id)
        if not user_data:
            return
        edited = update.edited_message
        if not edited or not edited.text:
            return
        updated = db.update_chat_message_text(edited.chat_id, edited.message_id, edited.text)
        if updated:
            logger.info(f"Synced edit for message {edited.message_id} in chat {edited.chat_id}")

    # Intent routing registry: adding a new intent means adding a value to
    # IntentResponse.intent, a section in the intent prompt, and an entry here.
    intent_handlers = {
        'RECOMMEND': handle_recommend_request,
        'ADD_MEDIA': handle_add_media_request,
        'INQUIRY': handle_inquiry_request,
    }

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("clear", clear_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.UpdateType.EDITED_MESSAGE, handle_edited_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    return db, jellyfin_client

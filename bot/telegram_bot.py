"""
Telegram Bot Handler Module

This module orchestrates the Telegram bot interface. It handles user messages,
processes LLM intent classification (inquiring about media or requesting recommendations),
renders interactive carousels of movies and shows, lazy-loads media metadata,
interacts with Sonarr/Radarr APIs, registers user feedback (watched/disliked),
and manages callback queries for inline button interactions.
"""

import logging
import requests
import json
import time
import re
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler
from openai import OpenAI
import chevron
import os
from bot.models import IntentResponse, RecommendationResponse, InquiryResponse
from bot.database import Database
from bot.translations import get_text
from bot.jellyfin import JellyfinClient
from bot.session_context import set_session_id, reset_session_id
from bot.llm_logging import log_llm_call
from bot.recommendation_pool import resolve_recommendation_sources
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
        logger.info("Jellyfin client initialized")
    else:
        logger.info("Jellyfin not configured, skipping watch history sync")

    tmdb_client = config.get('tmdb_client')
    if tmdb_client:
        logger.info("TMDB client initialized")
    else:
        logger.info("TMDB not configured, skipping discovery filtering")

    def resolve_arr(user_info: dict, media_type: str):
        """Return (url, key) for the user's configured Radarr or Sonarr instance."""
        arr_key = 'radarr' if media_type == 'movie' else 'sonarr'
        arr_map = config.get('radarrs' if media_type == 'movie' else 'sonarrs', {})
        name = user_info.get(arr_key, {}).get('name')
        instance = arr_map.get(name, {})
        return instance.get('url'), instance.get('key')

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = auth_func(update.effective_user.id)
        if not user_data: return
        context.user_data['user_info'] = user_data
        sent = await update.message.reply_text("🎬 Media Bot Online. Use /status to check services, or just ask me to add a movie/show!")
        add_to_history(update, context, "assistant", "🎬 Media Bot Online. Use /status to check services, or just ask me to add a movie/show!", sent)

    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = auth_func(update.effective_user.id)
        if not user_data: return
        context.user_data['user_info'] = user_data
        
        sonarr_url = config.get('sonarr_url')
        sonarr_key = config.get('sonarr_key')
        
        status_lines = []
        
        # Check Sonarr
        if sonarr_url and sonarr_key:
            try:
                resp = requests.get(f"{sonarr_url}/api/v3/system/status", headers={'X-Api-Key': sonarr_key}, timeout=5)
                if resp.status_code == 200:
                    status_lines.append("✅ Sonarr: Online")
                else:
                    status_lines.append(f"⚠️ Sonarr: Error {resp.status_code}")
            except Exception as e:
                status_lines.append(f"❌ Sonarr: Unreachable ({str(e)})")
        else:
            status_lines.append("ℹ️ Sonarr: Not configured")

        response_text = "\n".join(status_lines)
        sent = await update.message.reply_text(response_text)
        add_to_history(update, context, "assistant", response_text, sent)

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = auth_func(update.effective_user.id)
        if not user_data: return
        context.user_data['user_info'] = user_data
        if not openai_clients:
            sent = await update.message.reply_text("⚠️ LLM not configured. Cannot process request.")
            add_to_history(update, context, "assistant", "⚠️ LLM not configured. Cannot process request.", sent)
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
            # 1. Classify with LLM
            # Build messages: System + History
            system_content = load_prompt(agent_prompts.get('intent', {}))
            messages = [{"role": "system", "content": system_content}]
            
            # History from DB already includes the user message stored above.
            messages.extend(get_llm_history(update.effective_user.id))
            
            # Log the request
            logger.info(f"Sending LLM Request (Intent): {json.dumps(messages, ensure_ascii=False)}")
            
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

            if result.intent == 'RECOMMEND':
                await handle_recommend_request(update, context, result)
            
            elif result.intent == 'ADD_MEDIA':
                await handle_add_media_request(update, context, result)
            
            elif result.intent == 'INQUIRY':
                await handle_inquiry_request(update, context, result)
            
            else:
                resp_text = "🤔 I'm not sure what you want."
                sent = await update.message.reply_text(resp_text)
                add_to_history(update, context, "assistant", resp_text, sent)

        except Exception as e:
            session_status = 'failed'
            logger.error(f"Error processing message: {e}")
            sent = await update.message.reply_text("❌ Something went wrong processing your request.")
            add_to_history(update, context, "assistant", "❌ Something went wrong processing your request.", sent)
        finally:
            reset_session_id(ctx_token)
            if context.user_data.get('session_status') == 'failed':
                session_status = 'failed'
            session_duration_ms = int((time.time() - session_start) * 1000)
            db.complete_session(session_id, detected_intent, session_status, session_duration_ms)

    async def handle_inquiry_request(update: Update, context: ContextTypes.DEFAULT_TYPE, data: IntentResponse):
        user_text = update.message.text
        logger.info(f"Handling inquiry for: {user_text}")
        
        # Get user language preference
        user_info = context.user_data.get('user_info', {})
        user_lang = user_info.get('preferences', {}).get('language', 'en')
        thinking_msg = get_text(user_lang, 'thinking')
        
        await update.message.reply_text(thinking_msg)
        
        try:
            # Build messages: System + History
            system_content = load_prompt(agent_prompts.get('inquiry', {}), language=user_lang)
            messages = [{"role": "system", "content": system_content}]
            
            # Add history from DB
            messages.extend(get_llm_history(update.effective_user.id))
            
            logger.info(f"Sending LLM Request (Inquiry)")
            
            start_time = time.time()
            llm_cfg, current_client = get_agent_llm('inquiry')
            if not current_client:
                raise ValueError("No OpenAI client available for inquiry")
                
            kwargs = build_llm_kwargs(llm_cfg,
                model=llm_cfg.get('model', 'gpt-4.1-mini'),
                input=messages,
                text_format=InquiryResponse,
                tools=[{"type": "web_search"}]
            )
            response = current_client.responses.parse(**kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            
            parsed = response.output_parsed

            log_llm_call(
                db,
                session_id=context.user_data['session_id'],
                user_id=update.effective_user.id,
                user_message=user_text,
                prompt_name='inquiry',
                kwargs=kwargs,
                response=response,
                parsed=parsed,
                duration_ms=duration_ms,
                llm_name=llm_cfg.get('name'),
                pricing=llm_cfg.get('pricing'),
            )

            reply_text = parsed.reply_text
            
            sent = await update.message.reply_text(reply_text)
            add_to_history(update, context, "assistant", reply_text, sent)
            
            if parsed.items:
                await start_carousel(update, context, list(parsed.items), 'movie')
                add_to_history(update, context, "assistant", "Shared inquiry results carousel")
            
        except Exception as e:
            context.user_data['session_status'] = 'failed'
            logger.error(f"Inquiry error: {e}")
            sent = await update.message.reply_text("❌ Error generating response.")
            add_to_history(update, context, "assistant", "❌ Error generating response.", sent)

    async def handle_recommend_request(update: Update, context: ContextTypes.DEFAULT_TYPE, data: IntentResponse):
        query = data.query or 'something good'
        logger.info(f"Generating recommendations for: {query}")
        
        # Get user language preference
        user_info = context.user_data.get('user_info', {})
        user_lang = user_info.get('preferences', {}).get('language', 'en')
        thinking_msg = get_text(user_lang, 'thinking')
        
        await update.message.reply_text(thinking_msg)
        
        try:
             # Get user context for personalized recommendations
             user_info = context.user_data.get('user_info', {})
             user_name = user_info.get('name', '')
             user_prefs = user_info.get('preferences', {})
             user_lang = user_prefs.get('language', 'en')
             
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
             
             # Ask LLM for list with user context
             tmdb_candidates_data = []
             if tmdb_client:
                 recommendation_sources = resolve_recommendation_sources(user_prefs)
                 recent_tmdb_ids = db.get_recent_excluded_tmdb_ids(
                     user_id, recommendation_exclude_ttl_seconds
                 )
                 excluded_tmdb_ids = db.get_excluded_tmdb_ids(user_id) | recent_tmdb_ids
                 tmdb_candidates_list = tmdb_client.get_candidates(
                     recommendation_sources, user_lang, excluded_tmdb_ids
                 )
                 if tmdb_candidates_list:
                     tmdb_candidates_data = [{"items": tmdb_candidates_list}]
             
             prompt = load_prompt(agent_prompts.get('recommend', {}), 
                                query=query, 
                                user_name=user_name,
                                language=user_lang,
                                user_preferences=user_preferences,
                                user_guidelines=user_guidelines,
                                tmdb_candidates=tmdb_candidates_data,
                                watched_list=', '.join(watched_titles[:20]) if watched_titles else '',
                                disliked_list=', '.join(disliked_titles[:20]) if disliked_titles else '')
             logger.info(f"Sending LLM Request (Recommend): {prompt}")
             
             start_time = time.time()
             llm_cfg, current_client = get_agent_llm('recommend')
             if not current_client:
                 raise ValueError("No OpenAI client available for recommend")
                 
             kwargs = build_llm_kwargs(llm_cfg,
                model=llm_cfg.get('model', 'gpt-4o-mini'),
                input=[{"role": "user", "content": prompt}],
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
                 sent = await update.message.reply_text("❌ Couldn't generate recommendations.")
                 add_to_history(update, context, "assistant", "❌ Couldn't generate recommendations.", sent)
                 return
             
             # Filter out watched/disliked/recently recommended content
             recent_tmdb_ids = db.get_recent_excluded_tmdb_ids(
                 user_id, recommendation_exclude_ttl_seconds
             )
             recent_titles = db.get_recent_excluded_titles(
                 user_id, recommendation_exclude_ttl_seconds
             )
             excluded_titles = db.get_excluded_titles(user_id) | recent_titles

             def _is_excluded(item):
                 if item.title.lower() in excluded_titles:
                     return True
                 if item.original_title and item.original_title.lower() in excluded_titles:
                     return True
                 if item.tmdb_id and str(item.tmdb_id) in recent_tmdb_ids:
                     return True
                 return False

             all_items = parsed_response.items
             items = [item for item in all_items if not _is_excluded(item)]

             logger.info(
                 "Filtered recommendations: %d -> %d (excluded %d titles, %d recent TMDB ids)",
                 len(all_items),
                 len(items),
                 len(excluded_titles),
                 len(recent_tmdb_ids),
             )
             
             if not items:
                 sent = await update.message.reply_text("❌ Couldn't generate recommendations.")
                 add_to_history(update, context, "assistant", "❌ Couldn't generate recommendations.", sent)
                 return

             reply_markup = ReplyKeyboardMarkup([['Recommend more']], resize_keyboard=True, one_time_keyboard=False)
             
             await start_carousel(update, context, list(items), 'movie')
             db.record_recent_recommendations(user_id, items)
             add_to_history(update, context, "assistant", f"Shared recommendations carousel for '{query}'")

        except Exception as e:
             context.user_data['session_status'] = 'failed'
             logger.error(f"Recommendation error: {e}")
             sent = await update.message.reply_text("❌ Error generating recommendations.")
             add_to_history(update, context, "assistant", "❌ Error generating recommendations.", sent)

    async def handle_add_media_request(update: Update, context: ContextTypes.DEFAULT_TYPE, data: IntentResponse):
        title = data.title
        media_type = data.media_type # Default to movie
        
        if not title:
            sent = await update.message.reply_text("❓ I understood you want to add media, but I couldn't figure out the title.")
            add_to_history(update, context, "assistant", "❓ I understood you want to add media, but I couldn't figure out the title.", sent)
            return

        logger.info(f"Initiating search for '{title}' as {media_type}")

        user_info = context.user_data.get('user_info', {})

        if media_type == 'movie':
            url, key = resolve_arr(user_info, 'movie')
            if not url:
                await update.message.reply_text("⚠️ No Radarr instance configured for your account.")
                return
            await search_and_display(update, context, title, url, key, 'movie')

        elif media_type == 'series':
            url, key = resolve_arr(user_info, 'series')
            if not url:
                await update.message.reply_text("⚠️ No Sonarr instance configured for your account.")
                return
            await search_and_display(update, context, title, url, key, 'series')
        else:
             sent = await update.message.reply_text(f"❓ Ambiguous media type for '{title}'.")
             add_to_history(update, context, "assistant", f"Ambiguous media type for '{title}'.", sent)

    async def search_and_display(update: Update, context: ContextTypes.DEFAULT_TYPE, title: str, base_url: str, api_key: str, type_: str):
        endpoint = "movie" if type_ == "movie" else "series"
        lookup_endpoint = f"{base_url}/api/v3/{endpoint}/lookup"
        
        try:
            logger.info(f"Searching API: {lookup_endpoint} term={title}")
            params = {'term': title}
            resp = requests.get(lookup_endpoint, headers={'X-Api-Key': api_key}, params=params)
            resp.raise_for_status()
            results = resp.json()
            
            if not results:
                logger.info("Search returned 0 results.")
                sent = await update.message.reply_text(f"❌ No results found for '{title}' on {type_.capitalize()} DB.")
                add_to_history(update, context, "assistant", f"❌ No results found for '{title}' on {type_.capitalize()} DB.", sent)
                return
            
            # --- Filtering & Sorting ---
            filtered_results = []
            for item in results:
                status = item.get('status', '').lower()
                if status in ['announced', 'upcoming', 'tba']:
                    continue
                filtered_results.append(item)
            
            if not filtered_results:
                 sent = await update.message.reply_text(f"❌ No released media found for '**{title}**'.")
                 add_to_history(update, context, "assistant", f"❌ No released media found for '**{title}**'.", sent)
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
            sent = await update.message.reply_text(f"❌ Error communicating with {type_.capitalize()}.")
            add_to_history(update, context, "assistant", f"❌ Error communicating with {type_.capitalize()}.", sent)

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
            resp = requests.get(url, headers={'X-Api-Key': api_key}, params={'term': title})
            
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
            id_val = None  # LLM recommendations don't have IDs yet
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
        
        caption = f"🎬 **{t}** ({y})\n{overview}\n\n(Result {idx+1}/{total})"
        
        # Buttons - Two rows:
        # Row 1: [⬅️] [➕ Add / ✅ Added] [➡️]
        # Row 2: [▶️ Play on Jellyfin] or [👁️ Watched] [👎 Dislike]
        id_val = item.get('tmdbId') if type_ == 'movie' else item.get('tvdbId')
        
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
            if not already_available and item.get('id', 0) > 0:
                already_available = True
        
        # First row: Feedback actions & Add
        watched_data = make_safe_callback_data("WATCHED", type_, str(id_val or "0"), t)
        dislike_data = make_safe_callback_data("DISLIKE", type_, str(id_val or "0"), t)
        ignore_data = make_safe_callback_data("IGNORE", type_, str(id_val or "0"), t)
        
        action_row = [
            InlineKeyboardButton("👁️👍", callback_data=watched_data),
            InlineKeyboardButton("👁️👎", callback_data=dislike_data),
            InlineKeyboardButton("🚫", callback_data=ignore_data)
        ]
        
        if id_val:
            add_button = InlineKeyboardButton("✅ Added", callback_data="NOP") if already_available else InlineKeyboardButton("➕ Add", callback_data=f"ADD|{type_}|{id_val}")
            action_row.append(add_button)
            
        rows = [action_row]
            
        # Second row: Navigation
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
            rows.append([InlineKeyboardButton("▶️ Play on Jellyfin", url=jf_url)])
            
        reply_markup = InlineKeyboardMarkup(rows)
        
        try:
            from telegram import InputMediaPhoto
            msg = update.callback_query.message if not is_new else None
            
            if is_new:
                if remote_poster:
                     return await update.message.reply_photo(photo=remote_poster, caption=caption, parse_mode='Markdown', reply_markup=reply_markup)
                else:
                     return await update.message.reply_text(text=caption, parse_mode='Markdown', reply_markup=reply_markup)
            elif msg: 
                 if remote_poster:
                      if msg.photo:
                          await msg.edit_media(media=InputMediaPhoto(media=remote_poster, caption=caption, parse_mode='Markdown'), reply_markup=reply_markup)
                      else:
                          # Can't switch from text to media easily without deleting. 
                          # Ideally we delete and send new if types mismatch, but edit_message_text is safer for consistency.
                          # If we started with text and now have photo...
                          # For now, if msg.photo is None, stay text.
                          await msg.edit_text(text=caption, parse_mode='Markdown', reply_markup=reply_markup)
                 else:
                      if msg.photo:
                           # Had photo, now no photo. Edit caption? Or use placeholder?
                           # Edit caption
                           await msg.edit_caption(caption=caption, parse_mode='Markdown', reply_markup=reply_markup)
                      else:
                           await msg.edit_text(text=caption, parse_mode='Markdown', reply_markup=reply_markup)
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
            await query.answer("Unauthorized", show_alert=True)
            return
        context.user_data['user_info'] = user_data

        data = query.data
        logger.info(f"Callback received: {data}")

        if data.startswith("NAV|"):
            direction = data.split("|")[1]
            chat_id = query.message.chat_id
            message_id = query.message.message_id

            state = db.get_carousel_state(chat_id, message_id)
            if not state:
                await query.answer("This carousel has expired.", show_alert=True)
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
        
        if data.startswith("WATCHED|") or data.startswith("DISLIKE|") or data.startswith("IGNORE|"):
            # Format: WATCHED|type|id|title or DISLIKE|type|id|title or IGNORE|type|id|title
            parts = data.split("|")
            raw_action = parts[0].lower()
            content_type = parts[1]
            content_id = parts[2]
            title = parts[3] if len(parts) > 3 else "Unknown"
            
            # Normalize to canonical feedback_type values
            feedback_map = {"watched": "watched", "dislike": "disliked", "ignore": "ignored"}
            feedback_type = feedback_map.get(raw_action, raw_action)
            
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
            
            # Extract TMDB/TVDB IDs from callback data
            tmdb_id = content_id if content_type == "movie" and content_id != "0" else None
            tvdb_id = content_id if content_type == "series" and content_id != "0" else None
            
            # Save feedback to database
            db.add_feedback(
                user_id=user_id,
                content_id=content_id,
                content_type=content_type,
                title=title,
                feedback_type=feedback_type,
                tmdb_id=tmdb_id,
                tvdb_id=tvdb_id,
            )
            
            if feedback_type == "watched":
                feedback_msg = "✅ Marked as watched"
            elif feedback_type == "disliked":
                feedback_msg = "✅ Marked as disliked"
            else:
                feedback_msg = "✅ Ignored"
                
            await query.answer(feedback_msg, show_alert=False)
            logger.info(f"User {user_id} marked {title} as {feedback_type}")
            return

        if not data.startswith("ADD|"): 
            await query.answer()
            return

        await query.answer("Adding to library...") 
        
        _, type_, id_val = data.split("|")
        
        user_id = update.effective_user.id
        user_info = context.user_data.get('user_info', {})
        if type_ == 'movie':
             url, key = resolve_arr(user_info, 'movie')
             if not url:
                 await query.answer("⚠️ No Radarr configured for your account.", show_alert=True)
                 return
             quality_profile = user_info.get('radarr', {}).get('quality_profile')
             await perform_add(query, id_val, url, key, 'movie', user_id, quality_profile)
        else:
             url, key = resolve_arr(user_info, 'series')
             if not url:
                 await query.answer("⚠️ No Sonarr configured for your account.", show_alert=True)
                 return
             quality_profile = user_info.get('sonarr', {}).get('quality_profile')
             await perform_add(query, id_val, url, key, 'series', user_id, quality_profile)

    async def perform_add(query, id_val: str, base_url: str, api_key: str, type_: str, user_id: int = None, quality_profile: str = None):
        endpoint = "movie" if type_ == "movie" else "series"
        lookup_endpoint = f"{base_url}/api/v3/{endpoint}/lookup"
        add_endpoint = f"{base_url}/api/v3/{endpoint}"
        
        # Determine strict lookup term
        # Radarr: tmdb:<id>
        # Sonarr: tvdb:<id>
        term = f"tmdb:{id_val}" if type_ == 'movie' else f"tvdb:{id_val}"
        
        try:
            logger.info(f"Looking up item by ID: {term} in {base_url}")
            # 1. Lookup to get full payload
            params = {'term': term}
            resp_lookup = requests.get(lookup_endpoint, headers={'X-Api-Key': api_key}, params=params)
            resp_lookup.raise_for_status()
            results = resp_lookup.json()
            
            if not results:
                logger.error("Lookup by ID returned no results.")
                await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **Error: Item not found during add.**", parse_mode='Markdown')
                return
            
            candidate = results[0]
            
            # Check existing
            if candidate.get('id', 0) > 0: # Already managed
                 await query.edit_message_caption(caption=f"{query.message.caption}\n\n⚠️ **Already in library!**", parse_mode='Markdown')
                 logger.info(f"Item {candidate.get('title')} already exists.")
                 return

            # 2. Get Root Folder & Profile
            # Fetch Root Folders
            rf_resp = requests.get(f"{base_url}/api/v3/rootfolder", headers={'X-Api-Key': api_key})
            root_folders = rf_resp.json()
            if not root_folders:
                raise Exception("No Root Folders configured")
            root_path = root_folders[0]['path']
            
            # Fetch Quality Profile — match by name if specified, else use first
            qp_resp = requests.get(f"{base_url}/api/v3/qualityprofile", headers={'X-Api-Key': api_key})
            profiles = qp_resp.json()
            if not profiles:
                 raise Exception("No Quality Profiles configured")
            if quality_profile:
                matched = next(
                    (p for p in profiles if p.get('name', '').lower() == quality_profile.lower()),
                    None
                )
                if matched:
                    profile_id = matched['id']
                    logger.info(f"Using quality profile '{matched['name']}' (id={profile_id})")
                else:
                    profile_id = profiles[0]['id']
                    logger.warning(f"Quality profile '{quality_profile}' not found, falling back to '{profiles[0]['name']}'")
            else:
                profile_id = profiles[0]['id']
                logger.info(f"No quality profile specified, using first: '{profiles[0]['name']}'")

            # Prepare Payload
            payload = candidate
            payload['qualityProfileId'] = profile_id
            payload['rootFolderPath'] = root_path
            payload['monitored'] = True
            
            if type_ == 'movie':
                payload['addOptions'] = {'searchForMovie': True}
            else:
                payload['addOptions'] = {'searchForMissingEpisodes': True}
                payload['seasonFolder'] = True

            logger.info(f"Sending Add Payload for {candidate.get('title')}")
            resp_add = requests.post(add_endpoint, headers={'X-Api-Key': api_key}, json=payload)
            
            if resp_add.status_code == 201:
                logger.info("Add successful.")
                
                # Record the media request for webhook notifications
                # Store chat_id and message_id so webhook can later edit this card
                chat_id = query.message.chat_id
                message_id = query.message.message_id
                if user_id:
                    title = candidate.get('title', '')
                    tmdb_id = str(candidate.get('tmdbId', '')) if type_ == 'movie' else None
                    tvdb_id = str(candidate.get('tvdbId', '')) if type_ == 'series' else None
                    db.add_media_request(
                        telegram_id=user_id,
                        title=title,
                        media_type=type_,
                        tmdb_id=tmdb_id,
                        tvdb_id=tvdb_id,
                        chat_id=chat_id,
                        message_id=message_id
                    )
                
                # Keep nav row but replace Add with "⏳ Downloading" (no-op)
                current_markup = query.message.reply_markup
                if current_markup and current_markup.inline_keyboard:
                    new_rows = []
                    for row in current_markup.inline_keyboard:
                        new_row = []
                        for btn in row:
                            if btn.callback_data and btn.callback_data.startswith('ADD|'):
                                new_row.append(InlineKeyboardButton("⏳ Downloading", callback_data="NOP"))
                            else:
                                new_row.append(btn)
                        new_rows.append(new_row)
                    await query.edit_message_reply_markup(
                        reply_markup=InlineKeyboardMarkup(new_rows)
                    )
                else:
                    await query.edit_message_reply_markup(reply_markup=None)
            else:
                err_text = resp_add.text
                logger.error(f"Add failed: {resp_add.status_code} - {err_text}")
                await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **Failed to add.**", parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Exception during perform_add: {e}")
            # Try to inform user
            try:
                if query.message.caption:
                     await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ **Error occurred.**", parse_mode='Markdown')
                else:
                     await query.edit_message_text(text=f"{query.message.text}\n\n❌ **Error occurred.**", parse_mode='Markdown')
            except:
                pass


    async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Wipe the user's stored chat transcript and carousel state."""
        user_data = auth_func(update.effective_user.id)
        if not user_data:
            return
        context.user_data['user_info'] = user_data
        removed = db.clear_chat(update.effective_user.id)
        db.clear_user_carousels(update.effective_user.id)
        db.clear_recent_recommendations(update.effective_user.id)
        # Confirmation is transient and intentionally not stored in the transcript.
        await update.message.reply_text(f"🧹 Cleared {removed} stored messages. Starting fresh.")

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

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("clear", clear_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.UpdateType.EDITED_MESSAGE, handle_edited_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    return db, jellyfin_client

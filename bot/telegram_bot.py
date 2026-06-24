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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters, CallbackQueryHandler
from openai import OpenAI
import chevron
import os
from bot.models import IntentResponse, RecommendationResponse, InquiryResponse
from bot.database import Database
from bot.translations import get_text
from bot.jellyfin import JellyfinClient
logger = logging.getLogger(__name__)

def load_prompt(name, **kwargs):
    current_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(current_dir, 'prompts', f'{name}.mustache')
    with open(prompt_path, 'r') as f:
        return chevron.render(f, kwargs)

def add_to_history(context: ContextTypes.DEFAULT_TYPE, role: str, content: str):
    """Adds a message to the chat history, keeping only the last 30."""
    if 'history' not in context.chat_data:
        context.chat_data['history'] = []
    
    context.chat_data['history'].append({"role": role, "content": content})
    
    # Trim to last 30
    if len(context.chat_data['history']) > 30:
        context.chat_data['history'] = context.chat_data['history'][-30:]

def register_handlers(app: Application, config: dict, auth_func):
    """Registers commands for the Media (*Arr) bot"""
    
    # Initialize OpenAI client if configured
    llm_config = config.get('llm', {})
    client = None
    if llm_config.get('api_key') and llm_config.get('provider') == 'openai':
        client = OpenAI(api_key=llm_config.get('api_key'))
    else:
        logger.warning("OpenAI not configured. LLM features will be disabled.")
    
    # Initialize database
    db = Database()
    
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
        await update.message.reply_text("🎬 Media Bot Online. Use /status to check services, or just ask me to add a movie/show!")
        add_to_history(context, "assistant", "🎬 Media Bot Online. Use /status to check services, or just ask me to add a movie/show!")

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
        await update.message.reply_text(response_text)
        add_to_history(context, "assistant", response_text)

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = auth_func(update.effective_user.id)
        if not user_data: return
        context.user_data['user_info'] = user_data
        if not client:
            await update.message.reply_text("⚠️ LLM not configured. Cannot process request.")
            add_to_history(context, "assistant", "⚠️ LLM not configured. Cannot process request.")
            return

        user_text = update.message.text
        logger.info(f"Received message: {user_text}")

        # Add user message to history
        add_to_history(context, "user", user_text)

        try:
            # 1. Classify with LLM
            # Build messages: System + History
            system_content = load_prompt("intent_classification")
            messages = [{"role": "system", "content": system_content}]
            
            # Add history (excluding the one we just added? No, include it.)
            # Wait, we just added it. So history contains it.
            messages.extend(context.chat_data.get('history', []))
            
            # Log the request
            logger.info(f"Sending LLM Request (Intent): {json.dumps(messages, ensure_ascii=False)}")
            
            start_time = time.time()
            response = client.beta.chat.completions.parse(
                model=config.get('llm', {}).get('model', 'gpt-4o'),
                messages=messages,
                response_format=IntentResponse
            )
            duration_ms = int((time.time() - start_time) * 1000)
            
            result = response.choices[0].message.parsed
            logger.info(f"LLM Result Parsed: {result}")
            
            tokens = response.usage.total_tokens if getattr(response, 'usage', None) else 0
            try:
                db.log_llm_interaction(
                    user_id=update.effective_user.id,
                    user_message=user_text,
                    intent="CLASSIFY_INTENT",
                    llm_request=json.dumps(messages, ensure_ascii=False),
                    llm_response=json.dumps(result.dict(), ensure_ascii=False) if hasattr(result, 'dict') else str(result),
                    duration_ms=duration_ms,
                    model=response.model,
                    tokens=tokens
                )
            except Exception as log_e:
                logger.error(f"Failed to log LLM interaction: {log_e}")


            if result.intent == 'RECOMMEND':
                await handle_recommend_request(update, context, result)
            
            elif result.intent == 'ADD_MEDIA':
                await handle_add_media_request(update, context, result)
            
            elif result.intent == 'INQUIRY':
                await handle_inquiry_request(update, context, result)
            
            else:
                resp_text = "🤔 I'm not sure what you want."
                await update.message.reply_text(resp_text)
                add_to_history(context, "assistant", resp_text)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("❌ Something went wrong processing your request.")
            add_to_history(context, "assistant", "❌ Something went wrong processing your request.")

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
            system_content = load_prompt("inquiry", language=user_lang)
            messages = [{"role": "system", "content": system_content}]
            
            # Add history
            messages.extend(context.chat_data.get('history', []))
            
            logger.info(f"Sending LLM Request (Inquiry)")
            
            start_time = time.time()
            response = client.responses.parse(
                model=config.get('llm', {}).get('model', 'gpt-4.1-mini'),
                input=messages,
                text_format=InquiryResponse,
                tools=[{"type": "web_search"}]
            )
            duration_ms = int((time.time() - start_time) * 1000)
            
            parsed = response.output_parsed
            
            tokens = response.usage.total_tokens if getattr(response, 'usage', None) else 0
            try:
                db.log_llm_interaction(
                    user_id=update.effective_user.id,
                    user_message=user_text,
                    intent="INQUIRY",
                    llm_request=json.dumps(messages, ensure_ascii=False),
                    llm_response=json.dumps(parsed.dict(), ensure_ascii=False) if hasattr(parsed, 'dict') else str(parsed),
                    duration_ms=duration_ms,
                    model=response.model,
                    tokens=tokens
                )
            except Exception as log_e:
                logger.error(f"Failed to log LLM interaction: {log_e}")
                
            reply_text = parsed.reply_text
            
            await update.message.reply_text(reply_text)
            add_to_history(context, "assistant", reply_text)
            
            if parsed.items:
                context.user_data['search_results'] = parsed.items
                context.user_data['search_index'] = 0
                context.user_data['search_type'] = 'movie' # Defaulting to movie for mixed lists
                await send_carousel_card(update, context, is_new=True)
                add_to_history(context, "assistant", "Shared inquiry results carousel")
            
        except Exception as e:
            logger.error(f"Inquiry error: {e}")
            await update.message.reply_text("❌ Error generating response.")
            add_to_history(context, "assistant", "❌ Error generating response.")

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
                 discovery_filter = user_prefs.get('discovery_filter', {})
                 tmdb_candidates_list = tmdb_client.get_candidates(discovery_filter, user_lang)
                 if tmdb_candidates_list:
                     tmdb_candidates_data = [{"items": tmdb_candidates_list}]
             
             prompt = load_prompt("recommendation", 
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
             response = client.responses.parse(
                model=config.get('llm', {}).get('model', 'gpt-4o-mini'),
                input=[{"role": "user", "content": prompt}],
                text_format=RecommendationResponse,
                tools=[{"type": "web_search"}]
             )
             duration_ms = int((time.time() - start_time) * 1000)
             parsed_response = response.output_parsed
             logger.info(f"LLM Response Parsed (Recommend): {parsed_response}")
             
             tokens = response.usage.total_tokens if getattr(response, 'usage', None) else 0
             try:
                 db.log_llm_interaction(
                    user_id=update.effective_user.id,
                    user_message=query,
                    intent="RECOMMEND",
                    llm_request=prompt,
                    llm_response=json.dumps(parsed_response.dict(), ensure_ascii=False) if hasattr(parsed_response, 'dict') else str(parsed_response),
                    duration_ms=duration_ms,
                    model=response.model,
                    tokens=tokens
                 )
             except Exception as log_e:
                 logger.error(f"Failed to log LLM interaction: {log_e}")
             
             if not parsed_response or not parsed_response.items:
                 await update.message.reply_text("❌ Couldn't generate recommendations.")
                 add_to_history(context, "assistant", "❌ Couldn't generate recommendations.")
                 return
             
             # Filter out watched/disliked content by title
             user_id = update.effective_user.id
             excluded_titles = db.get_excluded_titles(user_id)
             
             # Keep as Pydantic models, filter by title (case-insensitive)
             all_items = parsed_response.items
             items = [item for item in all_items if item.title.lower() not in excluded_titles]
             
             logger.info(f"Filtered recommendations: {len(all_items)} -> {len(items)} (excluded {len(excluded_titles)} titles)")
             
             if not items:
                 await update.message.reply_text("❌ Couldn't generate recommendations.")
                 add_to_history(context, "assistant", "❌ Couldn't generate recommendations.")
                 return

             # Store in session (without IDs/Images yet)
             context.user_data['search_results'] = items
             context.user_data['search_index'] = 0
             context.user_data['search_type'] = 'movie' # Recommendations default to movie for now
             
             # context.user_data['search_type'] = 'movie' # Redundant line removed
             
             await send_carousel_card(update, context, is_new=True)
             add_to_history(context, "assistant", f"Shared recommendations carousel for '{query}'")

        except Exception as e:
             logger.error(f"Recommendation error: {e}")
             await update.message.reply_text("❌ Error generating recommendations.")
             add_to_history(context, "assistant", "❌ Error generating recommendations.")

    async def handle_add_media_request(update: Update, context: ContextTypes.DEFAULT_TYPE, data: IntentResponse):
        title = data.title
        media_type = data.media_type # Default to movie
        
        if not title:
            await update.message.reply_text("❓ I understood you want to add media, but I couldn't figure out the title.")
            add_to_history(context, "assistant", "❓ I understood you want to add media, but I couldn't figure out the title.")
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
             await update.message.reply_text(f"❓ Ambiguous media type for '{title}'.")
             add_to_history(context, "assistant", f"Ambiguous media type for '{title}'.")

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
                await update.message.reply_text(f"❌ No results found for '{title}' on {type_.capitalize()} DB.")
                add_to_history(context, "assistant", f"❌ No results found for '{title}' on {type_.capitalize()} DB.")
                return
            
            # --- Filtering & Sorting ---
            filtered_results = []
            for item in results:
                status = item.get('status', '').lower()
                if status in ['announced', 'upcoming', 'tba']:
                    continue
                filtered_results.append(item)
            
            if not filtered_results:
                 await update.message.reply_text(f"❌ No released media found for '**{title}**'.")
                 add_to_history(context, "assistant", f"❌ No released media found for '**{title}**'.")
                 return

            # Sort by Popularity
            filtered_results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            
            # Take top 5
            candidates = filtered_results[:5]
            
            # --- Store State for Carousel ---
            context.user_data['search_results'] = candidates
            context.user_data['search_index'] = 0
            context.user_data['search_type'] = type_
            
            # Send first card
            await send_carousel_card(update, context, is_new=True)
            add_to_history(context, "assistant", f"Shared search results carousel for '{title}'")

        except Exception as e:
            logger.error(f"Search Exception: {e}")
            await update.message.reply_text(f"❌ Error communicating with {type_.capitalize()}.")
            add_to_history(context, "assistant", f"❌ Error communicating with {type_.capitalize()}.")

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

    async def send_carousel_card(update: Update, context: ContextTypes.DEFAULT_TYPE, is_new: bool = False):
        results = context.user_data.get('search_results', [])
        idx = context.user_data.get('search_index', 0)
        type_ = context.user_data.get('search_type', 'movie')
        
        if not results or idx < 0 or idx >= len(results):
            return

        item = results[idx]
        total = len(results)
        
        # LAZY LOADING METADATA
        # Check if we have an ID (Radarr/Sonarr ID or TMDB/TVDB ID). 
        # Generated items might be Pydantic models or dicts from API.
        # Use getattr for Pydantic, dict.get for dicts
        lookup_title = None  # Will be set to original_title for Pydantic items
        if isinstance(item, dict):
            id_val = item.get('tmdbId') if type_ == 'movie' else item.get('tvdbId')
            t = item.get('title', 'N/A')
            y = item.get('year', 'N/A')
            overview = item.get('overview', 'No description available')
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
                if not isinstance(item, dict):
                    full_item['_display_title'] = t
                    full_item['_display_overview'] = overview
                results[idx] = full_item
                item = full_item
                context.user_data['search_results'] = results # Save back
            else:
                # Item not found in DB
                # If it was a Pydantic model, convert to dict to add 'overview'
                if not isinstance(item, dict):
                    item = item.model_dump() # Convert Pydantic to dict
                    results[idx] = item # Update in results
                    context.user_data['search_results'] = results
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
        
        # Navigation row
        nav_row = []
        if idx > 0:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data="NAV|PREV"))
        else:
            nav_row.append(InlineKeyboardButton("⬅️", callback_data="NOP"))  # Disabled
        
        if id_val:
            if already_available:
                nav_row.append(InlineKeyboardButton("✅ Added", callback_data="NOP"))
            else:
                nav_row.append(InlineKeyboardButton("➕ Add", callback_data=f"ADD|{type_}|{id_val}"))
        else:
            nav_row.append(InlineKeyboardButton("🚫 Not Found", callback_data="NOP"))
        
        if idx < total - 1:
            nav_row.append(InlineKeyboardButton("➡️", callback_data="NAV|NEXT"))
        else:
            nav_row.append(InlineKeyboardButton("➡️", callback_data="NOP"))  # Disabled
        
        # Second row
        rows = [nav_row]
        if jf_url:
            rows.append([InlineKeyboardButton("▶️ Play on Jellyfin", url=jf_url)])
        elif id_val and not already_available:
            watched_data = make_safe_callback_data("WATCHED", type_, str(id_val), t)
            dislike_data = make_safe_callback_data("DISLIKE", type_, str(id_val), t)
            rows.append([
                InlineKeyboardButton("👁️ Watched", callback_data=watched_data),
                InlineKeyboardButton("👎 Dislike", callback_data=dislike_data)
            ])
        reply_markup = InlineKeyboardMarkup(rows)
        
        try:
            from telegram import InputMediaPhoto
            msg = update.callback_query.message if not is_new else None
            
            if is_new:
                if remote_poster:
                     await update.message.reply_photo(photo=remote_poster, caption=caption, parse_mode='Markdown', reply_markup=reply_markup)
                else:
                     await update.message.reply_text(text=caption, parse_mode='Markdown', reply_markup=reply_markup)
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

        except Exception as ex:
            logger.error(f"Error sending/editing card: {ex}")

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
            idx = context.user_data.get('search_index', 0)
            
            if direction == "NEXT":
                context.user_data['search_index'] = idx + 1
            elif direction == "PREV":
                context.user_data['search_index'] = max(0, idx - 1)
            
            await send_carousel_card(update, context, is_new=False)
            await query.answer()
            return
        
        if data.startswith("WATCHED|") or data.startswith("DISLIKE|"):
            # Format: WATCHED|type|id|title or DISLIKE|type|id|title
            parts = data.split("|")
            feedback_type = parts[0].lower()
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
            
            # Save feedback to database
            db.add_feedback(
                user_id=user_id,
                content_id=content_id,
                content_type=content_type,
                title=title,
                feedback_type=feedback_type
            )
            
            feedback_msg = "✅ Marked as watched" if feedback_type == "watched" else "✅ Marked as disliked"
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


    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    return db, jellyfin_client

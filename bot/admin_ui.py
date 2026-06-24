import os
import json
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

def register_admin_routes(app: web.Application, db, users_config: list, messenger_name: str):
    """Registers admin UI and API routes on the provided aiohttp app"""
    
    # Define API handlers
    async def api_requests(request):
        try:
            limit = int(request.query.get('limit', 50))
            user_id_str = request.query.get('user_id')
            user_id = int(user_id_str) if user_id_str else None
            rows = db.get_recent_media_requests(limit=limit, user_id=user_id)
            return web.json_response(rows)
        except Exception as e:
            logger.error(f"Error fetching requests: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def api_feedback(request):
        try:
            limit = int(request.query.get('limit', 50))
            user_id_str = request.query.get('user_id')
            user_id = int(user_id_str) if user_id_str else None
            rows = db.get_recent_feedback(limit=limit, user_id=user_id)
            return web.json_response(rows)
        except Exception as e:
            logger.error(f"Error fetching feedback: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def api_llm_logs(request):
        try:
            limit = int(request.query.get('limit', 50))
            user_id_str = request.query.get('user_id')
            user_id = int(user_id_str) if user_id_str else None
            rows = db.get_recent_llm_logs(limit=limit, user_id=user_id)
            return web.json_response(rows)
        except Exception as e:
            logger.error(f"Error fetching LLM logs: {e}")
            return web.json_response({"error": str(e)}, status=500)
            
    async def api_users(request):
        try:
            rows = db.get_users_summary()
            
            # Map configuration data by user ID
            user_settings = {}
            for user in users_config:
                if user.get('messenger', {}).get('messenger_name') == messenger_name:
                    uid = user.get('messenger', {}).get('user_id')
                    if uid:
                        user_settings[uid] = {
                            "name": user.get('name', 'Unknown'),
                            "radarr_name": user.get('radarr', {}).get('name', 'N/A'),
                            "radarr_profile": user.get('radarr', {}).get('quality_profile', 'N/A'),
                            "sonarr_name": user.get('sonarr', {}).get('name', 'N/A'),
                            "sonarr_profile": user.get('sonarr', {}).get('quality_profile', 'N/A')
                        }

            enriched_rows = []
            for row in rows:
                r = dict(row)
                uid = r['user_id']
                settings = user_settings.get(uid, {})
                r['name'] = settings.get('name', f"{uid}")
                r['radarr_name'] = settings.get('radarr_name', 'N/A')
                r['radarr_profile'] = settings.get('radarr_profile', 'N/A')
                r['sonarr_name'] = settings.get('sonarr_name', 'N/A')
                r['sonarr_profile'] = settings.get('sonarr_profile', 'N/A')
                enriched_rows.append(r)

            return web.json_response(enriched_rows)
        except Exception as e:
            logger.error(f"Error fetching users summary: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def api_media_library(request):
        """Return unified media library (merged requests + feedback) for a user."""
        try:
            user_id_str = request.query.get('user_id')
            if not user_id_str:
                return web.json_response({"error": "user_id is required"}, status=400)
            user_id = int(user_id_str)
            limit = int(request.query.get('limit', 200))
            rows = db.get_user_media_library(user_id=user_id, limit=limit)
            return web.json_response(rows)
        except Exception as e:
            logger.error(f"Error fetching media library: {e}")
            return web.json_response({"error": str(e)}, status=500)

    # Add API routes
    app.router.add_get('/admin/api/requests', api_requests)
    app.router.add_get('/admin/api/feedback', api_feedback)
    app.router.add_get('/admin/api/llm-logs', api_llm_logs)
    app.router.add_get('/admin/api/users', api_users)
    app.router.add_get('/admin/api/media-library', api_media_library)
    
    # Define static files directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(base_dir, 'web')
    
    # Ensure web directory exists
    os.makedirs(web_dir, exist_ok=True)
    
    # Serve index.html on /admin
    async def admin_index(request):
        return web.FileResponse(os.path.join(web_dir, 'index.html'))
        
    app.router.add_get('/admin', admin_index)
    app.router.add_get('/admin/', admin_index)
    
    # Serve static assets (CSS, JS)
    app.router.add_static('/admin/static', web_dir)
    
    logger.info("Registered Admin UI routes")

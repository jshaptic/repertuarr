"""
Phrase key constants for the bot phrase catalog.

Centralizes string identifiers used by get_phrase() and YAML data files.
"""

# Onboarding / flow
WELCOME = "welcome"
RECOMMEND_BUTTON = "recommend_button"
THINKING_INQUIRY = "thinking_inquiry"
THINKING_RECOMMEND = "thinking_recommend"
THINKING_ADD_MEDIA = "thinking_add_media"
THINKING_LIST_EXTRACT = "thinking_list_extract"
UNKNOWN_INTENT = "unknown_intent"
REQUEST_ERROR = "request_error"
LLM_NOT_CONFIGURED = "llm_not_configured"
IMAGE_DOWNLOAD_ERROR = "image_download_error"

# Inquiry / recommend
INQUIRY_ERROR = "inquiry_error"
RECOMMEND_FAILED = "recommend_failed"
RECOMMEND_ERROR = "recommend_error"

# Add media / search
ADD_MEDIA_NO_TITLE = "add_media_no_title"
NO_RADARR = "no_radarr"
NO_SONARR = "no_sonarr"
AMBIGUOUS_MEDIA_TYPE = "ambiguous_media_type"
NO_SEARCH_RESULTS = "no_search_results"
NO_RELEASED_MEDIA = "no_released_media"
ARR_ERROR = "arr_error"
LIST_EXTRACT_FAILED = "list_extract_failed"
LIST_EXTRACT_EMPTY = "list_extract_empty"
MULTI_ADD_MISSES = "multi_add_misses"
ADD_ALL_DONE = "add_all_done"

# Carousel / callbacks
CAROUSEL_FOOTER = "carousel_footer"
INLINE_ADD = "inline_add"
INLINE_ADDED = "inline_added"
INLINE_ADD_ALL = "inline_add_all"
CAROUSEL_EXPIRED = "carousel_expired"
UNAUTHORIZED = "unauthorized"
FEEDBACK_WATCHED = "feedback_watched"
FEEDBACK_DISLIKED = "feedback_disliked"
FEEDBACK_IGNORED = "feedback_ignored"
ADDING_TO_LIBRARY = "adding_to_library"
ADD_NOT_FOUND = "add_not_found"
ALREADY_IN_LIBRARY = "already_in_library"
ADD_FAILED = "add_failed"
ADD_ERROR = "add_error"

# Status / misc
STATUS_SONARR_ONLINE = "status_sonarr_online"
STATUS_SONARR_ERROR = "status_sonarr_error"
STATUS_SONARR_UNREACHABLE = "status_sonarr_unreachable"
STATUS_SONARR_NOT_CONFIGURED = "status_sonarr_not_configured"
ADMIN_CLEAR_CHAT_NOTIFY = "admin_clear_chat_notify"
MESSENGER_HISTORY_SYNCED = "messenger_history_synced"

# Media type labels (lifecycle messages)
MEDIA_TYPE_MOVIE = "media_type_movie"
MEDIA_TYPE_SHOW = "media_type_show"

# Webhook
REQUEST_QUEUED = "request_queued"
DOWNLOAD_STARTED = "download_started"
DOWNLOAD_READY = "download_ready"
DOWNLOAD_READY_NO_URL = "download_ready_no_url"
DOWNLOAD_FAILED = "download_failed"
DOWNLOAD_UNAVAILABLE = "download_unavailable"

STYLE_SPECIFIC_KEYS = frozenset({
    THINKING_INQUIRY,
    THINKING_RECOMMEND,
    THINKING_ADD_MEDIA,
})

SUPPORTED_STYLES = (
    "default",
    "casual",
    "warm",
    "sarcastic",
    "wizarding",
)

SUPPORTED_LANGUAGES = (
    "en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "ko",
    "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi", "cs",
    "el", "he", "th", "vi", "id", "ms", "uk", "ro", "hu", "sk",
)

import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock, patch
import logging

# Mock dependencies
sys.modules['telegram'] = MagicMock()
sys.modules['telegram.ext'] = MagicMock()
sys.modules['openai'] = MagicMock()

# Setup logger
logging.basicConfig(level=logging.INFO)

async def test_interactive_flow():
    print("--- Testing Interactive Flow & Advanced Filters ---")
    
    from bots import media
    
    mock_update = AsyncMock()
    mock_update.effective_user.id = 123
    mock_update.message.text = "Add movie Matrix"
    mock_update.callback_query.message.photo = None # Initially no photo
    
    mock_context = MagicMock()
    # Use a real dict for user_data
    mock_context.user_data = {}
    
    # Mock config
    config = {
        'llm': {'provider': 'openai', 'api_key': 'k'},
        'radarr_url': 'http://r', 'radarr_key': 'k',
    }
    
    # 1. Test Search (Sort & Filter)
    print("\nTest 1: Search - Filtering Announced & Sorting")
    with patch('bots.media.requests') as mock_req:
        mock_req.get.return_value.status_code = 200
        # Return mixed results
        # A: Announced (Exclude)
        # B: Released, 10 votes (Popularity 10)
        # C: Released, 100 votes (Popularity 1000)
        # Note: The test code in last run failed sorting. 
        # Reason: `search_and_display` calls `send_carousel_card` immediately.
        # `send_carousel_card` invokes `lookup_metadata` lazily if id is missing.
        # BUT our search results mocks DO NOT have IDs? 
        # Wait, if ID is missing, `send_carousel_card` triggers lookup AND UPDATES user_data.
        # IF lookup returns a DIFFERENT item, it replaces it.
        # In my last content, I didn't mock lookup for Test 1.
        # So send_carousel_card called lookup -> Failed (NameResolutionError) -> Item kept as is?
        # NO. if lookup fails, item kept. 
        # But wait, why did sorting fail?
        # "User Data: ... [{'title': 'B_Low', ...}, {'title': 'B_Low', ...}]"
        # B_Low appears twice? 
        # Ah, maybe I messed up the mock return value list?
        # Let's verify the input list I used in `verify_interactive.py`.
        
        mock_req.get.return_value.json.return_value = [
             {'title': 'A_Announced', 'status': 'announced', 'year': 2026, 'popularity': 0, 'tmdbId': 1},
             {'title': 'B_Low', 'status': 'released', 'year': 2020, 'popularity': 10, 'tmdbId': 2},
             {'title': 'C_High', 'status': 'released', 'year': 2020, 'popularity': 1000, 'tmdbId': 3}
        ]
        # I Added tmdbId to avoid lazy lookup network call during pure search test.
        
        # Setup OpenAI mock for handle_message
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = \
            '{"intent": "ADD_MEDIA", "media_type": "movie", "title": "Test"}'
        
        with patch('bots.media.OpenAI', return_value=mock_client):
             # Register
             app = MagicMock()
             handlers = []
             app.add_handler.side_effect = lambda h: handlers.append(h)
             media.register_handlers(app, config, lambda x: True)
             
             # Get Text Handler
             # handle_message is passed to MessageHandler constructor.
             if not media.MessageHandler.called:
                 print("❌ MessageHandler not called")
                 return
             
             handler_func = media.MessageHandler.call_args[0][1]
             
             # Call handle_message
             await handler_func(mock_update, mock_context)
             
             # Verify send_carousel_card called
             # Check user_data
             results = mock_context.user_data.get('search_results')
             if not results:
                 print("❌ No results stored in user_data")
             else:
                 print(f"Stored {len(results)} results")
                 # Verify C_High is first (sorted by votes)
                 if results[0]['title'] == 'C_High':
                     print("✅ Sorting verified (High rated first)")
                 else:
                     print(f"❌ Sorting failed. First is {results[0]['title']}")
                 
                 # Verify A_Announced is missing
                 titles = [r['title'] for r in results]
                 if 'A_Announced' not in titles:
                     print("✅ Filtering verified (Announced excluded)")
                 else:
                     print("❌ Filtering failed. Announced present.")

    # 2. Test Carousel Navigation
    print("\nTest 2: Carousel Navigation")
    # Reset
    mock_context.user_data = {
        'search_results': [{'title': '1', 'tmdbId': 10}, {'title': '2', 'tmdbId': 11}], # Add IDs to avoid lazy lookup
        'search_index': 0,
        'search_type': 'movie'
    }
    
    mock_update.callback_query.data = "NAV|NEXT"
    
    if not media.CallbackQueryHandler.called:
         print("❌ CallbackQueryHandler not called")
         return
    
    cb_func = media.CallbackQueryHandler.call_args[0][0]
    
    # Mock edit calls
    mock_update.callback_query.message.edit_text = AsyncMock()
    
    await cb_func(mock_update, mock_context)
    
    print("New Index:", mock_context.user_data['search_index'])
    if mock_context.user_data['search_index'] == 1:
        print("✅ Navigation verified (Index moved to 1)")
    else:
        print("❌ Navigation failed")

    print("\nTest 3: Recommendation & Lazy Loading")
    # Reset mocks
    mock_context.user_data = {}
    
    # Setup LLM to return recommendation JSON
    rec_json = '{"items": [{"title": "RecMovie1", "year": 2025, "overview": "Cool"}, {"title": "RecMovie2", "year": 2024}]}'
    mock_client.chat.completions.create.return_value.choices[0].message.content = rec_json
    
    # Use handle_message logic but with "intent": "RECOMMEND"
    mock_client.chat.completions.create.side_effect = [
        MagicMock(choices=[MagicMock(message=MagicMock(content='{"intent": "RECOMMEND", "query": "comedy"}'))]), # Classification
        MagicMock(choices=[MagicMock(message=MagicMock(content=rec_json))]) # Generation
    ]
    
    # Mock lookup response for lazy loading
    with patch('bots.media.requests') as mock_req:
         # Mock lookup response
         mock_req.get.return_value.status_code = 200
         mock_req.get.return_value.json.return_value = [{'title': 'RecMovie1', 'year': 2025, 'tmdbId': 999, 'remotePoster': 'http://poster.jpg'}]
         
         await handler_func(mock_update, mock_context)
         
         # Verification
         items = mock_context.user_data.get('search_results')
         if items and len(items) == 2:
             print("✅ Recommendations generated (2 items)")
             if items[0].get('tmdbId') == 999:
                 print("✅ Lazy Loading verified (Metadata resolved for item 0)")
             else:
                 print(f"❌ Lazy Loading failed. Item 0 ID: {items[0].get('tmdbId')}")
         else:
             print("❌ Recommendations failed")
            
    print("\nTest 4: History Context Inclusion")
    # Reset
    mock_context.user_data = {}
    # Pre-populate history
    mock_context.chat_data = {
        'history': [
            {"role": "user", "content": "Old message 1"},
            {"role": "assistant", "content": "Old response 1"}
        ]
    }
    mock_update.message.text = "New request"
    
    # Mock LLM to just return simple intent
    mock_client.chat.completions.create.side_effect = None
    mock_client.chat.completions.create.return_value.choices[0].message.content = '{"intent": "ADD_MEDIA", "title": "New"}'
    
    await handler_func(mock_update, mock_context)
    
    # Check what was logged/sent
    # We can check the call args of mock_client.chat.completions.create
    call_args = mock_client.chat.completions.create.call_args
    if not call_args:
        print("❌ LLM not called")
    else:
        messages = call_args[1]['messages']
        # messages[0] is system
        # messages[1] should be Old message 1
        # messages[2] should be Old response 1
        # messages[3] should be New request (wait, handle_message adds it before calling LLM)
        
        if len(messages) >= 4:
            if messages[1]['content'] == "Old message 1" and messages[2]['content'] == "Old response 1":
                print("✅ History inclusion verified (Old messages present)")
            else:
                 print(f"❌ History verification failed. Messages: {messages}")
            
            # Verify new message added
            if messages[-1]['content'] == "New request":
                 print("✅ Current message addition verified")
            else:
                 print(f"❌ Current message missing from end: {messages[-1]}")
        else:
            print(f"❌ History missing. Len: {len(messages)}")

if __name__ == "__main__":
    asyncio.run(test_interactive_flow())

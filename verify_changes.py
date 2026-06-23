import asyncio
import logging
import sys
from main import run_bot

# Mock module
class MockModule:
    __name__ = "mock_bot"

async def test_disabled():
    logging.basicConfig(level=logging.INFO)
    print("Testing disabled bot...")
    # config with enabled: False
    config = {'enabled': False}
    app = await run_bot("token", config, MockModule, None)
    if app is None:
        print("SUCCESS: Disabled bot returned None")
    else:
        print("FAILURE: Disabled bot returned App")
        sys.exit(1)

async def test_enabled_no_token():
    print("Testing enabled bot with no token...")
    # config with enabled: True (default), but no token
    config = {'enabled': True}
    app = await run_bot(None, config, MockModule, None)
    if app is None:
         print("SUCCESS: Enabled bot with no token returned None (as expected due to missing token check)")
    else:
         print("FAILURE: expected None for missing token")
         sys.exit(1)

async def main():
    await test_disabled()
    await test_enabled_no_token()

if __name__ == "__main__":
    asyncio.run(main())

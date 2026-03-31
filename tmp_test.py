import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.search_service import search_logic

async def main():
    try:
        res = await search_logic("Quantum Computing")
        print("Success:", res)
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

import httpx
import json
import asyncio

async def main():
    payload = {
        "project_id": "test1",
        "user_query": "Design a surveillance drone carrying 2kg payload for 30 minutes"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/api/v1/solver/solve", json=payload, timeout=10.0)
        print("Status Code:", response.status_code)
        print("Response:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api.routes.blogs import router as blog_router

app = FastAPI()
app.include_router(blog_router, prefix="/api/blogs")

client = TestClient(app)

async def test_real_agent_integration():
    """Test the real agent with the live FastAPI route."""
    print("Starting integration test with real agent...")
    
    response = client.post("/api/blogs/research", json={
        "keywords": ["AI", "Machine Learning"],
        "max_results": 5,
        "quality_threshold": 0.7
    })
    
    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)
    else:
        print(f"Non-200 response: {response.status_code}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_real_agent_integration())

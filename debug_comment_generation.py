#!/usr/bin/env python3
"""
Debug script to test AI comment generation
"""

import asyncio
from src.seo_automation.agents.comment_writer import CommentWriterAgent

async def test_simple_comment():
    """Test a very simple comment generation"""
    agent = CommentWriterAgent()
    
    # Simple test data
    blog_data = {
        "title": "Getting Started with Kubernetes",
        "content": "Kubernetes is a powerful container orchestration platform that helps manage containerized applications at scale.",
        "url": "https://example.com/test"
    }
    
    content_analysis = {
        "relevance_score": 0.8,
        "key_topics": ["kubernetes", "containers"],
        "sentiment": "positive"
    }
    
    # Test the AI generation directly
    prompt = agent._build_comment_prompt(
        blog_data["title"],
        blog_data["content"], 
        content_analysis["key_topics"],
        ["kubernetes"],
        "engaging",
        content_analysis["sentiment"]
    )
    
    print("=== PROMPT ===")
    print(prompt)
    print("\n=== AI RESPONSE ===")
    
    try:
        response = await agent.execute_ai_task(prompt, "test", 300)
        print(f"Success: {response.success}")
        print(f"Result: '{response.result}'")
        print(f"Error: {response.error}")
        
        if response.result:
            print(f"Length: {len(response.result)}")
            print(f"Type: {type(response.result)}")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_comment())

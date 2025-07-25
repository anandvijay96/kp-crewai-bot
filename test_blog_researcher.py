#!/usr/bin/env python3
"""
Test script for BlogResearcher agent

This script tests the basic functionality of the BlogResearcher agent
without requiring full database setup.
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from seo_automation.agents.blog_researcher import BlogResearcher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_blog_researcher():
    """Test the BlogResearcher agent functionality."""
    print("🚀 Testing BlogResearcher Agent")
    print("=" * 50)
    
    try:
        # Initialize the agent
        print("📝 Initializing BlogResearcher agent...")
        agent = BlogResearcher()
        print(f"✅ Agent initialized: {agent}")
        
        # Test task execution
        print("\n🔍 Testing blog research task...")
        
        task = "Find high-quality blogs about cloud computing and DevOps for commenting opportunities"
        context = {
            'keywords': 'cloud computing devops kubernetes',
            'max_results': 5,
            'min_authority': 50
        }
        
        print(f"Task: {task}")
        print(f"Context: {context}")
        
        # Execute the task
        result = agent.execute(task, context)
        
        print("\n📊 Research Results:")
        print(f"✅ Success: {result['success']}")
        print(f"⏱️  Execution time: {result['execution_time']:.2f}s")
        
        if result['success']:
            research_data = result['result']
            print(f"\n🎯 Research Summary:")
            print(f"   Keywords: {research_data['search_keywords']}")
            print(f"   Discovered: {research_data['total_discovered']} blogs")
            print(f"   Analyzed: {research_data['total_analyzed']} blogs")
            print(f"   Qualified: {research_data['qualified_blogs']} blogs")
            print(f"   Stored: {research_data['stored_count']} blogs")
            
            print(f"\n📝 Found Blogs:")
            for i, blog in enumerate(research_data['blogs'], 1):
                print(f"   {i}. {blog['title']}")
                print(f"      URL: {blog['url']}")
                print(f"      Authority: {blog.get('estimated_authority', 'N/A')}")
                print(f"      Platform: {blog.get('platform', 'N/A')}")
                print(f"      Has Comments: {blog.get('has_comments', 'N/A')}")
                print(f"      Quality Score: {blog.get('qualification_score', 'N/A')}")
                print()
            
            print(f"📈 {research_data['summary']}")
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_tools():
    """Test individual tools separately."""
    print("\n🔧 Testing Individual Tools")
    print("=" * 50)
    
    try:
        from src.seo_automation.agents.blog_researcher import BlogSearchTool, BlogAnalysisTool
        
        # Test search tool
        print("🔍 Testing BlogSearchTool...")
        search_tool = BlogSearchTool()
        search_results = search_tool._run("cloud computing", 3)
        print(f"✅ Found {len(search_results)} blogs")
        
        for blog in search_results:
            print(f"   - {blog['title']} ({blog['domain']})")
        
        # Test analysis tool (using a mock URL since we don't want to make real requests in test)
        print(f"\n🔬 Testing BlogAnalysisTool...")
        analysis_tool = BlogAnalysisTool()
        
        # This will fail gracefully since it's a mock URL
        analysis_results = analysis_tool._run("https://example.com/blog")
        print(f"✅ Analysis completed (mock URL)")
        print(f"   Result: {analysis_results.get('error', 'Success')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤖 BlogResearcher Agent Test Suite")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test individual tools first
    tools_success = test_individual_tools()
    
    # Test the full agent
    agent_success = test_blog_researcher()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Tools Test: {'✅ PASSED' if tools_success else '❌ FAILED'}")
    print(f"   Agent Test: {'✅ PASSED' if agent_success else '❌ FAILED'}")
    print(f"   Overall: {'✅ ALL TESTS PASSED' if (tools_success and agent_success) else '❌ SOME TESTS FAILED'}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

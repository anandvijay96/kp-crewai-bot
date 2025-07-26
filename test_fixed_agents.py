#!/usr/bin/env python3
"""
Test script to verify that the aiohttp compatibility fix worked
and that agents can now be imported without falling back to mock data.
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_crewai_imports():
    """Test that CrewAI can be imported without errors."""
    print("🧪 Testing CrewAI imports...")
    try:
        from crewai import Agent, Task, Crew, Process
        print("✅ CrewAI core imports successful!")
        
        # Test creating a basic agent
        agent = Agent(
            role='Test Agent',
            goal='Test goal',
            backstory='Test backstory',
            verbose=True
        )
        print("✅ CrewAI Agent creation successful!")
        return True
    except Exception as e:
        print(f"❌ CrewAI import/creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_imports():
    """Test that our custom agents can be imported."""
    print("\n🧪 Testing custom agent imports...")
    
    agents_to_test = [
        ('BlogResearcher', 'seo_automation.agents.blog_researcher'),
        ('CampaignManagerAgent', 'seo_automation.agents.campaign_manager'), 
        ('CommentWriterAgent', 'seo_automation.agents.comment_writer'),
        ('ContentAnalyzer', 'seo_automation.agents.content_analyzer'),
        ('QualityReviewer', 'seo_automation.agents.quality_reviewer'),
    ]
    
    success_count = 0
    
    for agent_name, module_path in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            print(f"✅ {agent_name} import successful!")
            
            # Try to instantiate
            agent_instance = agent_class()
            print(f"✅ {agent_name} instantiation successful!")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {agent_name} failed: {e}")
            # Don't print full traceback for each agent to keep output clean
            
    print(f"\n📊 Agent Import Results: {success_count}/{len(agents_to_test)} agents working")
    return success_count == len(agents_to_test)

def test_mock_fallback_removed():
    """Verify that mock fallback is no longer triggered."""
    print("\n🧪 Testing that mock fallback is no longer used...")
    
    try:
        # This import would previously trigger the mock fallback
        from seo_automation.agents.blog_researcher import BlogResearcher
        
        # Check if it's the real implementation (has BaseAgent attributes)
        researcher = BlogResearcher()
        
        # Real CrewAI agents inherit from BaseAgent and have these attributes
        if hasattr(researcher, 'name') and hasattr(researcher, 'role') and hasattr(researcher, 'tools'):
            print("✅ Real BlogResearcher is being used (not mock)!")
            print(f"   Agent name: {researcher.name}")
            print(f"   Agent role: {researcher.role}")
            print(f"   Tools count: {len(researcher.tools) if researcher.tools else 0}")
            return True
        else:
            print("❌ Still using mock implementation")
            return False
            
    except Exception as e:
        print(f"❌ BlogResearcher test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔧 Testing aiohttp compatibility fixes for CrewAI agents")
    print("=" * 60)
    
    # Test 1: Basic CrewAI imports
    crewai_success = test_crewai_imports()
    
    # Test 2: Custom agent imports  
    agents_success = test_agent_imports()
    
    # Test 3: Verify mock fallback is no longer used
    mock_success = test_mock_fallback_removed()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏆 FINAL RESULTS:")
    print(f"✅ CrewAI Core: {'PASS' if crewai_success else 'FAIL'}")
    print(f"✅ Custom Agents: {'PASS' if agents_success else 'FAIL'}")
    print(f"✅ No Mock Fallback: {'PASS' if mock_success else 'FAIL'}")
    
    all_success = crewai_success and agents_success and mock_success
    
    if all_success:
        print("\n🎉 ALL TESTS PASSED! The aiohttp compatibility fix worked!")
        print("📝 The application should now use real agents instead of mock data.")
    else:
        print("\n❌ Some tests failed. Further investigation may be needed.")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

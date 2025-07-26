#!/usr/bin/env python3
"""
Trace the import error with aiohttp ConnectionTimeoutError
"""

import sys
import traceback
import os

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_basic_imports():
    """Test imports step by step to isolate the issue."""
    print("🔍 Testing step-by-step imports to isolate ConnectionTimeoutError issue")
    print("=" * 70)
    
    try:
        print("Step 1: Testing aiohttp import...")
        import aiohttp
        print(f"✅ aiohttp version: {aiohttp.__version__}")
        print(f"   ConnectionTimeoutError available: {hasattr(aiohttp, 'ConnectionTimeoutError')}")
        
        # Check what's actually available in aiohttp
        timeout_attrs = [attr for attr in dir(aiohttp) if 'timeout' in attr.lower() or 'error' in attr.lower()]
        print(f"   Available timeout/error attributes: {timeout_attrs}")
        
    except Exception as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    try:
        print("\nStep 2: Testing crewai import...")
        import crewai
        print(f"✅ crewai imported successfully")
        
    except Exception as e:
        print(f"❌ crewai import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False
    
    try:
        print("\nStep 3: Testing base agent import...")
        from seo_automation.core.base_agent import BaseSEOAgent
        print(f"✅ BaseSEOAgent imported successfully")
        
    except Exception as e:
        print(f"❌ BaseSEOAgent import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False
    
    try:
        print("\nStep 4: Testing tools imports...")
        from seo_automation.tools.web_scraper import WebScraper
        print(f"✅ WebScraper imported successfully")
        
        from seo_automation.tools.content_analysis import ContentAnalysisTool
        print(f"✅ ContentAnalysisTool imported successfully")
        
        from seo_automation.tools.seo_analyzer import SEOAnalyzer
        print(f"✅ SEOAnalyzer imported successfully")
        
        from seo_automation.tools.blog_validator import BlogValidatorTool
        print(f"✅ BlogValidatorTool imported successfully")
        
    except Exception as e:
        print(f"❌ Tools import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False
    
    try:
        print("\nStep 5: Testing enhanced blog researcher import...")
        from seo_automation.agents.enhanced_blog_researcher import EnhancedBlogResearcherAgent
        print(f"✅ EnhancedBlogResearcherAgent imported successfully")
        
        # Try to create an instance
        agent = EnhancedBlogResearcherAgent()
        print(f"✅ EnhancedBlogResearcherAgent instance created: {agent.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ EnhancedBlogResearcherAgent import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def check_dependency_versions():
    """Check versions of key dependencies."""
    print("\n🔍 Checking dependency versions:")
    print("=" * 50)
    
    dependencies = [
        'aiohttp', 'crewai', 'requests', 'beautifulsoup4', 
        'pydantic', 'fastapi', 'uvicorn', 'openai'
    ]
    
    for dep in dependencies:
        try:
            module = __import__(dep.replace('-', '_'))
            version = getattr(module, '__version__', 'Unknown')
            print(f"✅ {dep}: {version}")
        except ImportError:
            print(f"❌ {dep}: Not installed")
        except Exception as e:
            print(f"⚠️ {dep}: Error - {e}")

if __name__ == "__main__":
    print("🚀 Starting Import Error Trace")
    print("=" * 70)
    
    # Check dependency versions first
    check_dependency_versions()
    
    # Test imports step by step
    success = test_basic_imports()
    
    if success:
        print("\n🎉 All imports successful! The agent should work.")
    else:
        print("\n💥 Import issues detected. Need to fix dependencies.")
    
    sys.exit(0 if success else 1)

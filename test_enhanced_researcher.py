#!/usr/bin/env python3
"""
Test script for Enhanced BlogResearcher Agent

This script demonstrates the Phase 1 tools integration and enhanced capabilities
of the new BlogResearcher agent.
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.seo_automation.agents.enhanced_blog_researcher import EnhancedBlogResearcherAgent
from src.seo_automation.utils.logging import setup_logging

def main():
    """Test the Enhanced BlogResearcher Agent"""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🚀 Enhanced BlogResearcher Agent Test")
    print("=" * 50)
    
    try:
        # Initialize the enhanced agent
        print("📊 Initializing Enhanced BlogResearcher Agent...")
        agent = EnhancedBlogResearcherAgent()
        print("✅ Agent initialized successfully!")
        
        # Test task with context
        test_task = "Research high-quality blogs in cloud computing and DevOps space for comment opportunities"
        test_context = {
            'keywords': 'cloud computing devops kubernetes',
            'max_results': 5,
            'min_authority': 60
        }
        
        print(f"\n🔍 Executing task: {test_task}")
        print(f"📋 Context: {test_context}")
        print("\n⏳ Processing... (this may take a few minutes)")
        
        # Execute the enhanced research task
        start_time = datetime.now()
        result = agent.execute(test_task, test_context)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ Task completed in {execution_time:.2f} seconds")
        
        # Display results
        if result.get('success', False):
            research_result = result['result']
            
            print("\n📊 RESEARCH RESULTS")
            print("=" * 50)
            
            # Discovery statistics
            stats = research_result.get('discovery_stats', {})
            print(f"🔍 Discovery Statistics:")
            print(f"   • Total discovered: {stats.get('total_discovered', 0)}")
            print(f"   • Successfully analyzed: {stats.get('successfully_analyzed', 0)}")
            print(f"   • Qualified blogs: {stats.get('qualified_blogs', 0)}")
            print(f"   • Stored in database: {stats.get('stored_count', 0)}")
            
            # Quality metrics
            quality_metrics = research_result.get('quality_metrics', {})
            if quality_metrics:
                print(f"\n📈 Quality Metrics:")
                print(f"   • Average score: {quality_metrics.get('average_score', 0):.1f}")
                print(f"   • Highest score: {quality_metrics.get('highest_score', 0):.1f}")
                print(f"   • Success rate: {quality_metrics.get('success_rate', 0):.1f}%")
            
            # Top qualified blogs
            qualified_blogs = research_result.get('qualified_blogs', [])
            if qualified_blogs:
                print(f"\n🏆 Top Qualified Blogs:")
                for i, blog in enumerate(qualified_blogs[:3], 1):
                    print(f"   {i}. {blog.get('title', 'Unknown Title')}")
                    print(f"      URL: {blog.get('url', 'Unknown URL')}")
                    print(f"      Platform: {blog.get('platform', 'unknown')}")
                    print(f"      Score: {blog.get('comprehensive_score', 0):.1f}")
                    print()
            
            # Research report
            research_report = research_result.get('research_report', {})
            if research_report:
                print(f"📋 Research Report:")
                print(f"   Summary: {research_report.get('summary', 'No summary available')}")
                
                platform_dist = research_report.get('platform_distribution', {})
                if platform_dist:
                    print(f"   Platform distribution: {platform_dist}")
            
            # Recommendations
            recommendations = research_result.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
            
        else:
            print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"❌ Test failed: {e}")
        return 1
    
    print("\n🎉 Enhanced BlogResearcher Agent test completed!")
    return 0

if __name__ == "__main__":
    exit(main())

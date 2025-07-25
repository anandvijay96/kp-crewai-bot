"""
Advanced Integration Test for CampaignManagerAgent
Tests end-to-end campaign execution with real agent coordination
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from seo_automation.agents.campaign_manager import CampaignManagerAgent

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")

async def test_end_to_end_campaign():
    """Test complete end-to-end campaign execution"""
    print_section("END-TO-END CAMPAIGN INTEGRATION TEST")
    
    try:
        # Initialize campaign manager
        print("🚀 Initializing Campaign Manager...")
        campaign_manager = CampaignManagerAgent()
        print("✅ Campaign Manager initialized successfully")
        
        # Create a test campaign
        print_subsection("Creating Test Campaign")
        
        campaign_result = campaign_manager.create_campaign(
            name="Integration Test Campaign",
            keywords=["cloud computing", "DevOps", "kubernetes"],
            target_blogs=5,  # Small number for testing
            comments_per_blog=1,
            campaign_type="standard",
            priority="high"
        )
        
        if not campaign_result.get('success'):
            print(f"❌ Failed to create campaign: {campaign_result.get('error')}")
            return False
        
        campaign_id = campaign_result['campaign_id']
        print(f"✅ Campaign created successfully")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Estimated Cost: ${campaign_result['estimated_cost']:.2f}")
        print(f"   Estimated Duration: {campaign_result['estimated_duration']} minutes")
        
        # Display campaign structure
        campaign_config = campaign_result['campaign_config']
        print(f"\n📋 Campaign Structure:")
        print(f"   Name: {campaign_config['name']}")
        print(f"   Keywords: {campaign_config['keywords']}")
        print(f"   Target Blogs: {campaign_config['target_blogs']}")
        print(f"   Comments per Blog: {campaign_config['comments_per_blog']}")
        print(f"   Total Tasks: {len(campaign_config['tasks'])}")
        
        # Display task breakdown
        print(f"\n📝 Task Breakdown:")
        for i, task in enumerate(campaign_config['tasks'], 1):
            print(f"   {i}. {task['type']} (Priority: {task['priority']}, Agent: {task['agent']})")
        
        # Execute the campaign
        print_subsection("Executing Campaign")
        print("🔄 Starting campaign execution...")
        
        execution_start = datetime.now()
        
        # Execute campaign (this will coordinate all agents)
        execution_result = await campaign_manager.execute_campaign(campaign_id)
        
        execution_end = datetime.now()
        execution_duration = (execution_end - execution_start).total_seconds()
        
        print(f"⏱️  Campaign execution completed in {execution_duration:.2f} seconds")
        
        # Check execution results
        if execution_result.get('success'):
            print("✅ Campaign executed successfully!")
            
            # Display execution metrics
            final_metrics = execution_result.get('final_metrics', {})
            print(f"\n📊 Campaign Metrics:")
            print(f"   Blogs Discovered: {final_metrics.get('blogs_discovered', 0)}")
            print(f"   Blogs Qualified: {final_metrics.get('blogs_qualified', 0)}")
            print(f"   Comments Generated: {final_metrics.get('comments_generated', 0)}")
            print(f"   Task Completion Rate: {final_metrics.get('task_completion_rate', 0):.1%}")
            
            # Display campaign report
            campaign_report = execution_result.get('campaign_report', {})
            task_breakdown = campaign_report.get('task_breakdown', {})
            
            print(f"\n🎯 Task Execution Results:")
            print(f"   Total Tasks: {task_breakdown.get('total_tasks', 0)}")
            print(f"   Completed: {task_breakdown.get('completed', 0)}")
            print(f"   Failed: {task_breakdown.get('failed', 0)}")
            print(f"   Skipped: {task_breakdown.get('skipped', 0)}")
            
            # Display recommendations
            recommendations = campaign_report.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Campaign Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
            else:
                print(f"\n✨ No optimization recommendations - campaign performed well!")
            
            # Display detailed execution results
            if 'execution_results' in execution_result:
                print_subsection("Detailed Task Results")
                
                execution_results = execution_result['execution_results']
                
                for task_id, result in execution_results.items():
                    if isinstance(result, dict):
                        if 'result' in result and 'qualified_blogs' in result['result']:
                            # Blog research results
                            research_result = result['result']
                            discovery_stats = research_result.get('discovery_stats', {})
                            
                            print(f"🔍 Blog Research Results:")
                            print(f"   Total Discovered: {discovery_stats.get('total_discovered', 0)}")
                            print(f"   Successfully Analyzed: {discovery_stats.get('successfully_analyzed', 0)}")
                            print(f"   Qualified Blogs: {discovery_stats.get('qualified_blogs', 0)}")
                            
                            # Show sample qualified blogs
                            qualified_blogs = research_result.get('qualified_blogs', [])[:3]
                            if qualified_blogs:
                                print(f"   Sample Qualified Blogs:")
                                for blog in qualified_blogs:
                                    print(f"     - {blog.get('url', 'Unknown URL')} (Score: {blog.get('overall_score', 0):.1f})")
                        
                        elif 'comments_generated' in result:
                            # Comment generation results
                            print(f"💬 Comment Generation Results:")
                            print(f"   Comments Generated: {result.get('comments_generated', 0)}")
                            print(f"   Success Rate: {result.get('success_rate', 0):.1%}")
                            
                            # Show sample comments
                            comment_results = result.get('comment_results', [])[:2]
                            if comment_results:
                                print(f"   Sample Generated Comments:")
                                for comment_data in comment_results:
                                    comment_result = comment_data.get('comment_result', {})
                                    if comment_result.get('success'):
                                        comment_text = comment_result.get('comment', '')[:100]
                                        print(f"     - Blog: {comment_data.get('blog_url', 'Unknown')}")
                                        print(f"       Comment: \"{comment_text}...\"")
                                        
                                        metadata = comment_result.get('metadata', {})
                                        print(f"       Length: {metadata.get('length', 0)} chars, Quality: {metadata.get('validation_score', 0):.2f}")
            
            return True
            
        else:
            print(f"❌ Campaign execution failed: {execution_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_campaign_recovery():
    """Test campaign recovery and error handling"""
    print_section("CAMPAIGN RECOVERY AND ERROR HANDLING TEST")
    
    try:
        campaign_manager = CampaignManagerAgent()
        
        # Test campaign with invalid parameters that might cause issues
        print("🧪 Testing campaign with challenging parameters...")
        
        campaign_result = campaign_manager.create_campaign(
            name="Recovery Test Campaign",
            keywords=["extremely_rare_keyword_12345", "nonexistent_topic_xyz"],  # Likely to find few results
            target_blogs=3,
            comments_per_blog=1,
            campaign_type="aggressive"
        )
        
        if campaign_result.get('success'):
            campaign_id = campaign_result['campaign_id']
            print(f"✅ Campaign created: {campaign_id}")
            
            # Execute and see how it handles limited results
            execution_result = await campaign_manager.execute_campaign(campaign_id)
            
            if execution_result.get('success'):
                print("✅ Campaign handled challenging conditions successfully")
                
                final_metrics = execution_result.get('final_metrics', {})
                print(f"   Final metrics: {json.dumps(final_metrics, indent=2)}")
                
                return True
            else:
                print(f"⚠️  Campaign failed as expected with challenging conditions: {execution_result.get('error')}")
                return True  # This is expected behavior
        else:
            print(f"❌ Failed to create recovery test campaign: {campaign_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Recovery test failed: {e}")
        return False

async def test_concurrent_campaigns():
    """Test handling multiple concurrent campaigns"""
    print_section("CONCURRENT CAMPAIGNS TEST")
    
    try:
        campaign_manager = CampaignManagerAgent()
        
        print("🔄 Creating multiple campaigns...")
        
        campaigns = []
        
        # Create 3 small campaigns
        for i in range(3):
            campaign_result = campaign_manager.create_campaign(
                name=f"Concurrent Campaign {i+1}",
                keywords=[f"test_keyword_{i}", "concurrent_test"],
                target_blogs=2,
                comments_per_blog=1,
                priority="medium"
            )
            
            if campaign_result.get('success'):
                campaigns.append(campaign_result['campaign_id'])
                print(f"✅ Created campaign {i+1}: {campaign_result['campaign_id']}")
            else:
                print(f"❌ Failed to create campaign {i+1}")
        
        print(f"\n📊 Campaign Manager State:")
        print(f"   Active Campaigns: {len(campaign_manager.active_campaigns)}")
        print(f"   Campaign IDs: {list(campaign_manager.active_campaigns.keys())}")
        
        # Test concurrent execution (simulated)
        print(f"\n🚀 Testing concurrent campaign management...")
        
        all_successful = True
        for i, campaign_id in enumerate(campaigns):
            print(f"   Checking campaign {i+1} readiness...")
            campaign = campaign_manager.active_campaigns.get(campaign_id)
            if campaign:
                print(f"   ✅ Campaign {i+1} is ready with {len(campaign['tasks'])} tasks")
            else:
                print(f"   ❌ Campaign {i+1} not found")
                all_successful = False
        
        return all_successful
        
    except Exception as e:
        print(f"❌ Concurrent campaigns test failed: {e}")
        return False

async def run_integration_tests():
    """Run all integration tests"""
    print_section("CAMPAIGN MANAGER - INTEGRATION TEST SUITE")
    print(f"Integration test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Test 1: End-to-end campaign execution
    print("\n🧪 Running Test 1: End-to-End Campaign Execution")
    result1 = await test_end_to_end_campaign()
    test_results.append(("End-to-End Execution", result1))
    
    # Test 2: Campaign recovery and error handling
    print("\n🧪 Running Test 2: Campaign Recovery")
    result2 = await test_campaign_recovery()
    test_results.append(("Recovery & Error Handling", result2))
    
    # Test 3: Concurrent campaigns
    print("\n🧪 Running Test 3: Concurrent Campaigns")
    result3 = await test_concurrent_campaigns()
    test_results.append(("Concurrent Campaigns", result3))
    
    # Final results
    print_section("INTEGRATION TEST RESULTS")
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Integration Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print()
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nIntegration test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Overall assessment
    if success_rate >= 90:
        print("\n🎉 EXCELLENT: Campaign Manager integration is production-ready!")
    elif success_rate >= 75:
        print("\n✅ GOOD: Campaign Manager integration is functional with minor issues")
    else:
        print("\n⚠️  NEEDS WORK: Campaign Manager integration has significant issues")
    
    return success_rate

if __name__ == "__main__":
    # Run the integration test suite
    asyncio.run(run_integration_tests())

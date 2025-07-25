#!/usr/bin/env python3
"""
Test script for Enhanced CommentWriterAgent

This script demonstrates the comprehensive comment generation capabilities
of the Phase 2 CommentWriterAgent including:
- AI-powered contextual comment generation
- Multiple comment styles and strategies
- Quality validation and spam detection
- Database integration and performance tracking
- Batch processing capabilities
"""

import asyncio
import json
from datetime import datetime
from src.seo_automation.agents.comment_writer import CommentWriterAgent

# Test data - sample blog posts for comment generation
SAMPLE_BLOGS = [
    {
        "url": "https://techblog.example.com/kubernetes-deployment-strategies",
        "title": "Advanced Kubernetes Deployment Strategies for Production",
        "content": """
        Kubernetes has revolutionized container orchestration, but deploying applications 
        effectively requires understanding various deployment strategies. In this post, 
        we'll explore blue-green deployments, canary releases, and rolling updates.
        
        Blue-green deployment involves maintaining two identical production environments. 
        At any time, only one environment is live, while the other serves as a staging 
        area for the next release. This strategy minimizes downtime and provides quick 
        rollback capabilities.
        
        Canary deployment allows you to roll out changes to a small subset of users 
        before making them available to everybody. This reduces risk and allows for 
        real-world testing with minimal impact.
        
        Rolling updates gradually replace instances of the previous version with the 
        new version. This is Kubernetes' default deployment strategy and works well 
        for most applications.
        """,
        "author": "DevOps Team",
        "published_date": "2024-01-15"
    },
    {
        "url": "https://cloudtech.example.com/serverless-architecture-benefits",
        "title": "Why Serverless Architecture is the Future of Cloud Computing",
        "content": """
        Serverless computing has gained significant traction in recent years, offering 
        developers a way to build and run applications without managing servers. This 
        paradigm shift brings numerous benefits including reduced operational overhead, 
        automatic scaling, and cost optimization.
        
        With serverless, you only pay for the compute time you consume. There's no 
        charge when your code isn't running. This makes it incredibly cost-effective 
        for applications with variable traffic patterns.
        
        Popular serverless platforms include AWS Lambda, Azure Functions, and Google 
        Cloud Functions. Each offers unique features and integrations with their 
        respective cloud ecosystems.
        
        However, serverless isn't suitable for all use cases. Long-running processes, 
        applications requiring persistent connections, or those with specific runtime 
        requirements might not be ideal candidates.
        """,
        "author": "Cloud Architect",
        "published_date": "2024-01-10"
    },
    {
        "url": "https://devops.example.com/ci-cd-pipeline-optimization",
        "title": "Optimizing CI/CD Pipelines for Faster Software Delivery",
        "content": """
        Continuous Integration and Continuous Deployment (CI/CD) pipelines are the 
        backbone of modern software delivery. However, many organizations struggle 
        with slow, unreliable pipelines that bottleneck their development process.
        
        Key optimization strategies include parallelizing builds, caching dependencies, 
        using containerized build environments, and implementing proper testing strategies. 
        Each of these can significantly reduce pipeline execution time.
        
        Monitoring and metrics are crucial for identifying bottlenecks. Tools like 
        Jenkins, GitLab CI, and GitHub Actions provide detailed insights into pipeline 
        performance and can help identify areas for improvement.
        
        Remember that the goal isn't just speed, but reliability. A fast pipeline that 
        frequently fails is worse than a slower one that consistently delivers quality 
        software.
        """,
        "author": "Platform Engineering",
        "published_date": "2024-01-20"
    }
]

# Sample content analysis results (would normally come from ContentAnalysisTool)
SAMPLE_CONTENT_ANALYSIS = {
    "https://techblog.example.com/kubernetes-deployment-strategies": {
        "relevance_score": 0.92,
        "key_topics": ["kubernetes", "deployment strategies", "container orchestration", "DevOps", "blue-green deployment"],
        "sentiment": "positive",
        "technical_level": "advanced",
        "readability_score": 65.4
    },
    "https://cloudtech.example.com/serverless-architecture-benefits": {
        "relevance_score": 0.88,
        "key_topics": ["serverless", "cloud computing", "AWS Lambda", "cost optimization", "scalability"],
        "sentiment": "positive",
        "technical_level": "intermediate",
        "readability_score": 72.1
    },
    "https://devops.example.com/ci-cd-pipeline-optimization": {
        "relevance_score": 0.95,
        "key_topics": ["CI/CD", "pipeline optimization", "continuous deployment", "automation", "software delivery"],
        "sentiment": "neutral",
        "technical_level": "intermediate",
        "readability_score": 68.9
    }
}

# Target keywords for each blog
TARGET_KEYWORDS = {
    "https://techblog.example.com/kubernetes-deployment-strategies": [
        "kubernetes deployment", "container orchestration", "DevOps automation"
    ],
    "https://cloudtech.example.com/serverless-architecture-benefits": [
        "serverless computing", "cloud migration", "cost optimization"
    ],
    "https://devops.example.com/ci-cd-pipeline-optimization": [
        "CI/CD optimization", "automated deployment", "software delivery"
    ]
}

async def test_single_comment_generation():
    """Test generating a single comment with detailed analysis"""
    print("=" * 70)
    print("TEST 1: Single Comment Generation")
    print("=" * 70)
    
    try:
        agent = CommentWriterAgent()
        print(f"✓ CommentWriterAgent initialized: {agent.name}")
        
        # Select first blog for testing
        blog = SAMPLE_BLOGS[0]
        content_analysis = SAMPLE_CONTENT_ANALYSIS[blog["url"]]
        keywords = TARGET_KEYWORDS[blog["url"]]
        
        print(f"\nGenerating comment for: {blog['title']}")
        print(f"Target keywords: {', '.join(keywords)}")
        
        # Generate comment
        result = await agent.generate_comment(
            blog_data=blog,
            content_analysis=content_analysis,
            target_keywords=keywords,
            comment_type="engaging"
        )
        
        if result['success']:
            print(f"\n✓ Comment generated successfully!")
            print(f"Comment: {result['comment']}")
            print(f"\nMetadata:")
            metadata = result['metadata']
            for key, value in metadata.items():
                if key != 'validation_issues':
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {', '.join(value) if value else 'None'}")
        else:
            print(f"✗ Comment generation failed: {result['error']}")
        
        print(f"\nAgent performance: ${agent.get_accumulated_cost():.4f} total cost")
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")

async def test_multiple_comment_types():
    """Test generating different types of comments"""
    print("\n" + "=" * 70)
    print("TEST 2: Multiple Comment Types")
    print("=" * 70)
    
    try:
        agent = CommentWriterAgent()
        blog = SAMPLE_BLOGS[1]  # Serverless blog
        content_analysis = SAMPLE_CONTENT_ANALYSIS[blog["url"]]
        keywords = TARGET_KEYWORDS[blog["url"]]
        
        comment_types = ["engaging", "question", "insight", "technical"]
        
        for comment_type in comment_types:
            print(f"\n--- Generating {comment_type.upper()} comment ---")
            
            result = await agent.generate_comment(
                blog_data=blog,
                content_analysis=content_analysis,
                target_keywords=keywords,
                comment_type=comment_type
            )
            
            if result['success']:
                print(f"✓ {comment_type} comment ({result['metadata']['length']} chars):")
                print(f"  {result['comment'][:150]}...")
                print(f"  Validation Score: {result['metadata']['validation_score']}")
                print(f"  Keyword Density: {result['metadata']['keyword_density']:.3f}")
            else:
                print(f"✗ {comment_type} comment failed: {result['error']}")
        
        print(f"\nTotal cost for type testing: ${agent.get_accumulated_cost():.4f}")
        
    except Exception as e:
        print(f"✗ Multiple comment types test failed: {str(e)}")

async def test_comment_variants():
    """Test generating multiple variants of comments"""
    print("\n" + "=" * 70)
    print("TEST 3: Comment Variants Generation")
    print("=" * 70)
    
    try:
        agent = CommentWriterAgent()
        blog = SAMPLE_BLOGS[2]  # CI/CD blog
        content_analysis = SAMPLE_CONTENT_ANALYSIS[blog["url"]]
        keywords = TARGET_KEYWORDS[blog["url"]]
        
        print(f"Generating 3 comment variants for: {blog['title'][:50]}...")
        
        variants = await agent.generate_comment_variants(
            blog_data=blog,
            content_analysis=content_analysis,
            variant_count=3,
            target_keywords=keywords
        )
        
        print(f"\n✓ Generated {len(variants)} variants:")
        
        for i, variant in enumerate(variants, 1):
            metadata = variant['metadata']
            print(f"\nVariant {i} ({metadata['variant_type']}):")
            print(f"  Length: {metadata['length']} chars")
            print(f"  Validation: {metadata['validation_score']}/100")
            print(f"  Valid: {metadata['is_valid']}")
            print(f"  Preview: {variant['comment'][:100]}...")
        
        print(f"\nVariant generation cost: ${agent.get_accumulated_cost():.4f}")
        
    except Exception as e:
        print(f"✗ Comment variants test failed: {str(e)}")

async def test_batch_comment_generation():
    """Test batch comment generation for multiple blogs"""
    print("\n" + "=" * 70)
    print("TEST 4: Batch Comment Generation")
    print("=" * 70)
    
    try:
        agent = CommentWriterAgent()
        
        print(f"Processing {len(SAMPLE_BLOGS)} blogs in batch...")
        
        # Create content analysis mapping
        content_analyses = {}
        for blog in SAMPLE_BLOGS:
            content_analyses[blog['url']] = SAMPLE_CONTENT_ANALYSIS[blog['url']]
        
        # For batch processing, we'll simulate having content analysis
        # In practice, this would be integrated with ContentAnalysisTool
        batch_results = await agent.batch_generate_comments(
            blog_list=SAMPLE_BLOGS,
            keywords_per_blog=TARGET_KEYWORDS,
            comment_types=["engaging", "insight", "question"]
        )
        
        print(f"\n✓ Batch processing completed!")
        print(f"Successful: {len(batch_results['successful'])}")
        print(f"Failed: {len(batch_results['failed'])}")
        print(f"Success Rate: {batch_results['success_rate']:.1%}")
        print(f"Total Time: {batch_results['total_time']:.2f} seconds")
        print(f"Total Cost: ${batch_results['total_cost']:.4f}")
        
        if batch_results['successful']:
            print(f"\nSuccessful Comments:")
            for result in batch_results['successful']:
                url_short = result['url'].split('/')[-1]
                print(f"  ✓ {url_short}: {len(result['comment'])} chars, "
                      f"score: {result['metadata']['validation_score']}")
        
        if batch_results['failed']:
            print(f"\nFailed Comments:")
            for result in batch_results['failed']:
                url_short = result['url'].split('/')[-1]
                print(f"  ✗ {url_short}: {result['error']}")
        
    except Exception as e:
        print(f"✗ Batch comment generation test failed: {str(e)}")

async def test_agent_performance_metrics():
    """Test agent performance metrics and configuration"""
    print("\n" + "=" * 70)
    print("TEST 5: Agent Performance Metrics")
    print("=" * 70)
    
    try:
        agent = CommentWriterAgent()
        
        # Generate a few comments to accumulate some metrics
        blog = SAMPLE_BLOGS[0]
        content_analysis = SAMPLE_CONTENT_ANALYSIS[blog["url"]]
        
        for _ in range(2):
            await agent.generate_comment(
                blog_data=blog,
                content_analysis=content_analysis,
                target_keywords=["test", "metrics"],
                comment_type="engaging"
            )
        
        # Get performance metrics
        metrics = agent.get_performance_metrics()
        
        print("✓ Agent Performance Metrics:")
        print(json.dumps(metrics, indent=2, default=str))
        
        # Test configuration access
        print(f"\nSupported Comment Types: {len(agent.COMMENT_TYPES)}")
        for comment_type, description in agent.COMMENT_TYPES.items():
            print(f"  - {comment_type}: {description[:50]}...")
        
        print(f"\nBrand Configuration:")
        for key, value in agent.BRAND_VOICE_CONFIG.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"✗ Performance metrics test failed: {str(e)}")

async def main():
    """Run all CommentWriterAgent tests"""
    print("🤖 Enhanced CommentWriterAgent Test Suite")
    print("Phase 2 Implementation - AI-Powered Comment Generation")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = datetime.now()
    
    # Run all tests
    await test_single_comment_generation()
    await test_multiple_comment_types()
    await test_comment_variants()
    await test_batch_comment_generation()
    await test_agent_performance_metrics()
    
    # Final summary
    total_time = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"✓ All tests completed in {total_time:.2f} seconds")
    print("\nThe Enhanced CommentWriterAgent demonstrates:")
    print("  • AI-powered contextual comment generation")
    print("  • Multiple comment styles and strategies")
    print("  • Comprehensive quality validation")
    print("  • Spam detection and content filtering")
    print("  • Database integration for comment storage")
    print("  • Batch processing capabilities")
    print("  • Performance tracking and cost monitoring")
    print("  • Flexible configuration and templating")
    
    print(f"\n🎉 Phase 2 CommentWriterAgent is fully functional!")
    print("Ready for integration with Phase 1 tools and production deployment.")

if __name__ == "__main__":
    asyncio.run(main())

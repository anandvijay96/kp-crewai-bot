# Google Custom Search API Setup Guide

This guide will walk you through setting up the Google Custom Search API for free blog discovery using your **existing Google Cloud project** (the same one used for Vertex AI).

## Prerequisites
- Existing Google Cloud account with Vertex AI project
- Access to Google Cloud Console
- $300 free credits available

## Step 1: Use Your Existing Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project selector at the top
3. **Select your existing project** (the one you're using for Vertex AI)
4. You should see your project name in the header

> ✅ **Advantage**: Using the same project keeps everything organized and uses your existing $300 free credits!

## Step 2: Enable Custom Search JSON API

1. In the Google Cloud Console, go to the [API Library](https://console.cloud.google.com/apis/library)
2. Search for "Custom Search API"
3. Click on "Custom Search JSON API"
4. Click "Enable"

## Step 3: Create API Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "API Key"
3. Copy the generated API key
4. (Optional but recommended) Click "Restrict Key" to limit usage:
   - Under "Application restrictions", select "None" for now
   - Under "API restrictions", select "Restrict key" and choose "Custom Search JSON API"
   - Click "Save"

## Step 4: Create a Custom Search Engine

1. Go to [Google Custom Search](https://cse.google.com/cse/)
2. Click "Add" to create a new search engine
3. In "Sites to search", enter `*` (asterisk) to search the entire web
4. Give your search engine a name (e.g., "Blog Discovery Engine")
5. Click "Create"
6. Click "Control Panel" for your new search engine
7. Copy the "Search engine ID" (looks like: `017576662512468239146:omuauf_lfve`)

## Step 5: Configure Search Engine Settings

1. In the Control Panel, go to "Setup" → "Basics"
2. Make sure "Search the entire web" is enabled
3. Go to "Setup" → "Advanced" 
4. Under "WebSearch Settings", enable "Search the entire web"
5. Click "Update"

## Step 6: Set Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials (this will be added to your existing Vertex AI configuration):
   ```env
   # Existing Vertex AI configuration
   GOOGLE_APPLICATION_CREDENTIALS=./credentials/vertex-ai-key.json
   GOOGLE_CLOUD_PROJECT=kp-seo-blog-automator
   VERTEX_AI_LOCATION=us-central1
   
   # New Custom Search API credentials
   GOOGLE_SEARCH_API_KEY=your_actual_api_key_here
   GOOGLE_SEARCH_CSE_ID=your_search_engine_id_here
   ```

   > **Note**: Both Vertex AI and Custom Search API will use the same Google Cloud project and billing account.

## Step 7: Test the Setup

Run the test script to verify everything works:

```bash
python test_scraping.py
```

## Usage Limits & Cost Estimation

### Free Tier Limits:
- **100 queries per day** for free
- After that: $5 per 1000 queries (up to 10k queries per day max)

### Cost Estimation with Your $300 Credits:
- **Free daily usage**: 100 queries = $0
- **Paid usage**: 1000 queries = $5
- **Your $300 credits can cover**: ~60,000 additional queries (beyond free tier)
- **Example usage**: 500 queries/day would cost ~$2/day, lasting ~150 days with your credits

### Combined with Vertex AI Costs:
- Vertex AI: ~$0.01-0.10 per query (depending on model)
- Custom Search: $0.005 per query (after free tier)
- **Total estimated cost per blog research session**: $0.015-0.105 per query

### Tips to Stay Within Free Limits:
- Use specific, targeted keywords
- Cache results when possible
- Combine with DuckDuckGo search for more coverage
- Monitor usage in Google Cloud Console
- Start with free tier (100/day) and monitor actual usage patterns

## Troubleshooting

### Common Issues:

1. **"API key not valid"**
   - Check that the API key is correct
   - Ensure Custom Search JSON API is enabled
   - Verify API key restrictions

2. **"Invalid CSE ID"**
   - Double-check the Custom Search Engine ID
   - Ensure the CSE is set to search the entire web

3. **"Quota exceeded"**
   - You've hit the daily 100 query limit
   - Wait until the next day or upgrade to paid plan

4. **No search results**
   - Check that "Search the entire web" is enabled in CSE settings
   - Try different search queries
   - Verify the search engine is active

### Testing Individual Components:

To test just the Google Search API:
```bash
python -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from services.scraping.search_engines import SearchEngineManager

async def test():
    async with SearchEngineManager() as mgr:
        mgr._load_api_keys()
        results = await mgr.search_google('machine learning blog', 3)
        print(f'Found {len(results)} results')
        for r in results:
            print(f'  {r[\"title\"]} - {r[\"domain\"]}')

asyncio.run(test())
"
```

## Cost Management

Monitor your usage at:
- [Google Cloud Console](https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas)

Set up billing alerts:
1. Go to [Billing](https://console.cloud.google.com/billing)
2. Click "Budgets & alerts"  
3. Create a budget with alerts at 50%, 90% of your desired spend

## Next Steps

Once the Google Custom Search API is working:
1. Test the complete blog scraping workflow
2. Adjust search queries for better blog discovery
3. Fine-tune DA/PA filtering thresholds
4. Consider implementing result caching to reduce API calls

## Support

If you encounter issues:
1. Check the Google Cloud Console error logs
2. Review the API quotas and usage
3. Verify all environment variables are set correctly
4. Test with simple queries first before complex searches

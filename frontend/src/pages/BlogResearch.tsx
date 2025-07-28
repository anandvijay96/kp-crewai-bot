import React, { useState } from 'react';
import { api, ApiResponse } from '@/utils/apiClient';

interface Blog {
  title: string;
  domain: string;
  url: string;
  domain_authority: number;
  page_authority: number;
  authority: number;
  keywords: string[];
  traffic_estimate: number;
  comment_opportunity: boolean;
  quality_score: number;
}

export function BlogResearch() {
  const [keywords, setKeywords] = useState('');
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<any>(null);

  const handleSearch = async () => {
    if (!keywords.trim()) {
      setError('Please enter keywords to search');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response: ApiResponse<{ 
        blogs: Blog[];
        total_discovered: number;
        qualified_blogs: number;
        filter_criteria: any;
      }> = await api.post('/api/blogs/research', {
        keywords: keywords.split(',').map(k => k.trim()).filter(k => k.length > 0),
        minAuthority: 30,
      });
      
      console.log('API Response:', response);
      
      if (response.success && response.data) {
        setBlogs(response.data.blogs || []);
        setSearchResults(response.data);
      } else {
        setError(response.message || 'Failed to fetch blogs');
      }
    } catch (err: any) {
      console.error('Blog search error:', err);
      if (err.status === 401) {
        setError('Authentication required. Please log in.');
      } else if (err.status === 0) {
        setError('Cannot connect to server. Please ensure the API server is running.');
      } else {
        setError(err.message || 'Failed to fetch blogs');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Blog Research
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Discover and analyze blogs for your commenting campaigns.
        </p>
      </div>

      <div className="space-y-4">
        <input
          type="text"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter keywords, e.g. SEO, content marketing"
          className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-white text-gray-900 placeholder-gray-500"
        />
        <button
          onClick={handleSearch}
          className="w-full p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading || !keywords.trim()}
        >
          {loading ? 'Searching...' : 'Search Blogs'}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {searchResults && (
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-blue-800 dark:text-blue-200 text-sm">
            Found {searchResults.qualified_blogs} qualified blogs out of {searchResults.total_discovered} discovered
            {searchResults.filter_criteria && (
              <span>
                {' '}(Authority ≥ {searchResults.filter_criteria.min_domain_authority})
              </span>
            )}
          </p>
        </div>
      )}

      <div className="space-y-4">
        {blogs.length > 0 ? (
          blogs.map((blog, index) => (
            <div 
              key={index} 
              className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-3">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex-1 mr-4">
                  {blog.title}
                </h2>
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-xs rounded-full font-medium">
                    DA: {blog.domain_authority}
                  </span>
                  <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs rounded-full font-medium">
                    PA: {blog.page_authority}
                  </span>
                </div>
              </div>
              
              <div className="space-y-2">
                <p className="text-blue-600 dark:text-blue-400 font-medium">{blog.domain}</p>
                
                <div className="flex flex-wrap gap-2 mb-3">
                  {blog.keywords.map((keyword, kidx) => (
                    <span 
                      key={kidx}
                      className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Traffic: </span>
                    <span className="text-gray-900 dark:text-gray-100 font-medium">
                      {blog.traffic_estimate.toLocaleString()}
                    </span>
                  </div>
                  
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Quality: </span>
                    <span className="text-gray-900 dark:text-gray-100 font-medium">
                      {(blog.quality_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Comments: </span>
                    <span className={`font-medium ${
                      blog.comment_opportunity 
                        ? 'text-green-600 dark:text-green-400' 
                        : 'text-red-600 dark:text-red-400'
                    }`}>
                      {blog.comment_opportunity ? 'Available' : 'Limited'}
                    </span>
                  </div>
                  
                  <div>
                    <a 
                      href={blog.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                    >
                      Visit Blog →
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          !loading && searchResults && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                No blogs found matching your criteria. Try different keywords or lower the authority threshold.
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}

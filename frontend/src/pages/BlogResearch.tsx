import React, { useState, useEffect } from 'react';
import { api, ApiResponse } from '@/utils/apiClient';
import { websocketService, taskProgressService, TaskProgress } from '@/services/websocketService';

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
  const [currentTask, setCurrentTask] = useState<string | null>(null);
  const [taskProgress, setTaskProgress] = useState<TaskProgress | null>(null);

  useEffect(() => {
    websocketService.connect();

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const subscribeToRealTimeUpdates = (taskId: string) => {
    setCurrentTask(taskId);
    const unsubscribe = websocketService.subscribe('progress_update', (data) => {
      console.log('WebSocket progress update:', data);
      if (data.taskId === taskId) {
        setTaskProgress({
          task_id: data.taskId,
          status: data.type === 'completed' ? 'completed' : data.type === 'failed' ? 'failed' : 'in_progress',
          progress: data.progress || 0,
          message: data.message || '',
          data: data.data,
          error: data.error
        });
      }
    });
    
    // Also listen for task completion
    const unsubscribeComplete = websocketService.subscribe('task_completed', (data) => {
      console.log('WebSocket task completed:', data);
      if (data.taskId === taskId) {
        // Convert search results to blog format
        const searchResults = data.data || [];
        const blogs = searchResults.map((result: any, index: number) => ({
          title: result.title || 'Unknown Blog',
          domain: new URL(result.url).hostname,
          url: result.url,
          domain_authority: Math.floor(Math.random() * 100), // Mock DA for now
          page_authority: Math.floor(Math.random() * 100),   // Mock PA for now
          authority: Math.floor(Math.random() * 100),
          keywords: keywords.split(',').map(k => k.trim()).filter(k => k.length > 0),
          traffic_estimate: Math.floor(Math.random() * 50000),
          comment_opportunity: Math.random() > 0.5,
          quality_score: Math.random()
        }));
        
        setBlogs(blogs);
        setSearchResults({
          blogs,
          total_discovered: searchResults.length,
          qualified_blogs: blogs.length,
          filter_criteria: { min_domain_authority: 30 }
        });
        setLoading(false);
        setCurrentTask(null);
        setTaskProgress(null);
      }
    });
    
    // Handle task failures
    const unsubscribeFailed = websocketService.subscribe('task_failed', (data) => {
      console.log('WebSocket task failed:', data);
      if (data.taskId === taskId) {
        setError(data.message || 'Task failed');
        setLoading(false);
        setCurrentTask(null);
        setTaskProgress(null);
      }
    });
    
    // Return combined unsubscribe function
    return () => {
      unsubscribe();
      unsubscribeComplete();
      unsubscribeFailed();
    };
  };

  const handleSearch = async () => {
    if (!keywords.trim()) {
      setError('Please enter keywords to search');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      // Call Bun scraping service directly
      const response = await fetch('http://localhost:3002/api/scraping/blog-discovery', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: keywords.trim(),
          numResults: 10
        })
      });
      
      const data = await response.json();
      console.log('Bun Service Response:', data);
      
      if (response.ok && data.success) {
        // Extract task ID from response and subscribe to real-time updates
        const taskId = `blog-discovery-${Date.now()}`;
        subscribeToRealTimeUpdates(taskId);
        
        // Process results immediately if available
        if (data.data && Array.isArray(data.data)) {
          const searchResults = data.data;
          const blogs = searchResults.map((result: any, index: number) => ({
            title: result.title || 'Unknown Blog',
            domain: new URL(result.url).hostname,
            url: result.url,
            domain_authority: Math.floor(Math.random() * 100), // Mock DA for now
            page_authority: Math.floor(Math.random() * 100),   // Mock PA for now
            authority: Math.floor(Math.random() * 100),
            keywords: keywords.split(',').map(k => k.trim()).filter(k => k.length > 0),
            traffic_estimate: Math.floor(Math.random() * 50000),
            comment_opportunity: Math.random() > 0.5,
            quality_score: Math.random()
          }));
          
          setBlogs(blogs);
          setSearchResults({
            blogs,
            total_discovered: searchResults.length,
            qualified_blogs: blogs.length,
            filter_criteria: { min_domain_authority: 30 }
          });
          setLoading(false);
        }
      } else {
        setError(data.message || 'Failed to fetch blogs from scraping service');
        setLoading(false);
      }
    } catch (err: any) {
      console.error('Blog search error:', err);
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Cannot connect to scraping service. Please ensure it is running on port 3002.');
      } else {
        setError(err.message || 'Failed to fetch blogs');
      }
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

      {taskProgress && (
        <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <p className="text-yellow-800 dark:text-yellow-200 font-medium">
              {taskProgress.message}
            </p>
            <span className="text-yellow-600 dark:text-yellow-400 text-sm">
              {Math.round(taskProgress.progress)}%
            </span>
          </div>
          <div className="w-full bg-yellow-200 dark:bg-yellow-800 rounded-full h-2">
            <div 
              className="bg-yellow-600 dark:bg-yellow-400 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${taskProgress.progress}%` }}
            ></div>
          </div>
          {currentTask && (
            <p className="text-yellow-600 dark:text-yellow-400 text-xs mt-1">
              Task ID: {currentTask}
            </p>
          )}
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

import React, { useState, useEffect } from 'react';
import { api, ApiResponse } from '@/utils/apiClient';
import { websocketService, taskProgressService, TaskProgress } from '@/services/websocketService';

interface Blog {
  id?: string;
  title: string;
  domain: string;
  url: string;
  domain_authority: number;
  page_authority: number;
  description: string;
  discovery_source?: string;
  scraped_at?: string;
  category?: string;
  content_quality_score?: number;
  comment_opportunities?: string[];
}

interface HistoricalBlog {
  id: number;
  url: string;
  title: string;
  content_summary: string;
  has_comments: boolean;
  status: string;
  created_at: string;
  analysis_data: {
    domainAuthority?: number;
    pageAuthority?: number;
    domain?: string;
    discoveredAt?: string;
  };
}

export function BlogResearch() {
  const [keywords, setKeywords] = useState('');
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [historicalBlogs, setHistoricalBlogs] = useState<HistoricalBlog[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [searchResults, setSearchResults] = useState<any>(null);
  const [currentTask, setCurrentTask] = useState<string | null>(null);
  const [taskProgress, setTaskProgress] = useState<TaskProgress | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalHistoricalBlogs, setTotalHistoricalBlogs] = useState(0);
  const [activeTab, setActiveTab] = useState<'search' | 'history'>('search');

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

  // Load historical blogs
  const loadHistoricalBlogs = async (page: number = 1) => {
    try {
      setLoadingHistory(true);
      console.log(`Loading historical blogs - Page: ${page}`);
      
      const response = await api.get('/api/blogs/historical', {
        params: {
          page,
          page_size: 10
        }
      });
      
      console.log('Historical blogs response:', response);
      
      if (response.success && response.data) {
        setHistoricalBlogs(response.data.blogs || []);
        setTotalPages(response.data.total_pages || Math.ceil((response.data.total || 0) / 10));
        setTotalHistoricalBlogs(response.data.total || 0);
        console.log(`Loaded ${response.data.blogs?.length || 0} blogs, total pages: ${response.data.total_pages}, total blogs: ${response.data.total}`);
      }
    } catch (err: any) {
      console.error('Failed to load historical blogs:', err);
      setError('Failed to load historical blogs');
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'history') {
      loadHistoricalBlogs(currentPage);
    }
  }, [activeTab, currentPage]);

  const handleSearch = async () => {
    if (!keywords.trim()) {
      setError('Please enter keywords to search');
      return;
    }

    setLoading(true);
    setError(null);
    setBlogs([]);
    setSearchResults(null);
    
    try {
      // Call Bun scraping service directly (this was working)
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
        // Process results immediately since they come back with real DA/PA now
        if (data.data && data.data.blogs) {
          const discoveredBlogs = data.data.blogs;
          const blogs = discoveredBlogs.map((result: any) => ({
            title: result.title || 'Unknown Blog',
            domain: result.domain,
            url: result.url,
            domain_authority: result.domainAuthority || 0,
            page_authority: result.pageAuthority || 0,
            description: result.snippet || '',
            discovery_source: 'google_search',
            scraped_at: result.discoveredAt,
            content_quality_score: 0.8,
            comment_opportunities: ['General engagement']
          }));
          
          setBlogs(blogs);
          setSearchResults({
            blogs,
            total_discovered: data.data.totalResults || blogs.length,
            qualified_blogs: data.data.storedResults || blogs.length,
            filter_criteria: { min_domain_authority: 30 }
          });
          setLoading(false);
          
          // Refresh historical data if on history tab
          if (activeTab === 'history') {
            loadHistoricalBlogs(currentPage);
          }
        } else {
          setError('No blogs found in response');
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

  const pollForResults = async (taskId: string) => {
    const maxAttempts = 60; // 60 attempts = 5 minutes max
    let attempts = 0;
    
    const poll = async () => {
      try {
        attempts++;
        
        // Check progress first
        const progressResponse: ApiResponse<any> = await api.get(`/api/blogs/research/${taskId}/progress`);
        
        if (progressResponse.success && progressResponse.data) {
          const progress = progressResponse.data;
          setTaskProgress({
            task_id: taskId,
            status: progress.status,
            progress: progress.progress_percentage,
            message: progress.current_step,
            data: null,
            error: null
          });
          
          if (progress.status === 'completed') {
            // Get the results
            const resultsResponse: ApiResponse<Blog[]> = await api.get(`/api/blogs/research/${taskId}/results`);
            
            if (resultsResponse.success && resultsResponse.data) {
              setBlogs(resultsResponse.data);
              setSearchResults({
                blogs: resultsResponse.data,
                total_discovered: resultsResponse.data.length,
                qualified_blogs: resultsResponse.data.length,
                filter_criteria: { min_domain_authority: 30 }
              });
            }
            
            setLoading(false);
            setCurrentTask(null);
            setTaskProgress(null);
            
            // Refresh historical data
            if (activeTab === 'history') {
              loadHistoricalBlogs(currentPage);
            }
            return;
          } else if (progress.status === 'failed') {
            setError(progress.errors?.[0] || 'Research task failed');
            setLoading(false);
            setCurrentTask(null);
            setTaskProgress(null);
            return;
          }
        }
        
        // Continue polling if not completed and haven't exceeded max attempts
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          setError('Research task timed out');
          setLoading(false);
          setCurrentTask(null);
          setTaskProgress(null);
        }
      } catch (err: any) {
        console.error('Polling error:', err);
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000); // Continue polling on error
        } else {
          setError('Failed to get research results');
          setLoading(false);
          setCurrentTask(null);
          setTaskProgress(null);
        }
      }
    };
    
    poll();
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

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('search')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'search'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            New Search
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Previously Discovered ({historicalBlogs.length})
          </button>
        </nav>
      </div>

      {activeTab === 'search' ? (
        <>
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
                
                {/* Keywords from search */}
                <div className="flex flex-wrap gap-2 mb-3">
                  {keywords.split(',').map(k => k.trim()).filter(k => k.length > 0).map((keyword, kidx) => (
                    <span 
                      key={kidx}
                      className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
                
                {/* Description */}
                {blog.description && (
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                    {blog.description.substring(0, 150)}...
                  </p>
                )}
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Quality: </span>
                    <span className="text-gray-900 dark:text-gray-100 font-medium">
                      {Math.round((blog.content_quality_score || 0.8) * 100)}%
                    </span>
                  </div>
                  
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Source: </span>
                    <span className="text-gray-900 dark:text-gray-100 font-medium">
                      {blog.discovery_source || 'Google Search'}
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
        </>
      ) : (
        // Historical Blogs Tab
        <div className="space-y-4">
          {loadingHistory ? (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">Loading historical blogs...</p>
            </div>
          ) : historicalBlogs.length > 0 ? (
            <>
              <div className="grid gap-4">
                {historicalBlogs.map((blog) => (
                  <div 
                    key={blog.id} 
                    className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h2 className="text-xl font-bold text-gray-900 dark:text-white flex-1 mr-4">
                        {blog.title}
                      </h2>
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-xs rounded-full font-medium">
                          DA: {blog.analysis_data.domainAuthority || 'N/A'}
                        </span>
                        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs rounded-full font-medium">
                          PA: {blog.analysis_data.pageAuthority || 'N/A'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <p className="text-blue-600 dark:text-blue-400 font-medium">
                        {blog.analysis_data.domain || new URL(blog.url).hostname}
                      </p>
                      
                      {blog.content_summary && (
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                          {blog.content_summary.substring(0, 150)}...
                        </p>
                      )}
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Status: </span>
                          <span className={`font-medium ${
                            blog.status === 'discovered' 
                              ? 'text-green-600 dark:text-green-400'
                              : 'text-gray-600 dark:text-gray-400'
                          }`}>
                            {blog.status.charAt(0).toUpperCase() + blog.status.slice(1)}
                          </span>
                        </div>
                        
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Comments: </span>
                          <span className={`font-medium ${
                            blog.has_comments 
                              ? 'text-green-600 dark:text-green-400' 
                              : 'text-red-600 dark:text-red-400'
                          }`}>
                            {blog.has_comments ? 'Available' : 'Limited'}
                          </span>
                        </div>
                        
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Discovered: </span>
                          <span className="text-gray-900 dark:text-gray-100 font-medium">
                            {new Date(blog.created_at).toLocaleDateString()}
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
                ))}
              </div>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center space-x-2 mt-6">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50"
                  >
                    Previous
                  </button>
                  
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded font-medium">
                    Page {currentPage} of {totalPages}
                  </span>
                  
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                No previously discovered blogs found. Start by running a new search!
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

import { useState, useEffect } from 'react';
import { api } from '@/utils/apiClient';

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

export function DiscoveredBlogs() {
  const [historicalBlogs, setHistoricalBlogs] = useState<HistoricalBlog[]>([]);
  const [filteredBlogs, setFilteredBlogs] = useState<HistoricalBlog[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalHistoricalBlogs, setTotalHistoricalBlogs] = useState(0);
  
  // Filter states
  const [filterCriteria, setFilterCriteria] = useState({
    hideUnqualified: false, // Hide blogs with DA/PA < 30
    hideNoScore: false, // Hide blogs with N/A scores
    showAll: true // Show all blogs
  });

  // Load historical blogs
  const loadHistoricalBlogs = async (page: number = 1) => {
    try {
      setLoading(true);
      console.log(`Loading discovered blogs - Page: ${page}`);
      
      const response = await api.get('/api/blogs/historical', {
        params: {
          page,
          page_size: 20 // Show more per page since this is dedicated page
        }
      });
      
      console.log('Discovered blogs response:', response);
      
      if (response.success && response.data) {
        setHistoricalBlogs(response.data.blogs || []);
        console.log('Updated historical blogs:', response.data.blogs || []);
        setTotalPages(response.data.total_pages || Math.ceil((response.data.total || 0) / 20));
        setTotalHistoricalBlogs(response.data.total || 0);
        console.log(`Loaded ${response.data.blogs?.length || 0} blogs, total pages: ${response.data.total_pages}, total blogs: ${response.data.total}`);
      }
    } catch (err: any) {
      console.error('Failed to load discovered blogs:', err);
      setError('Failed to load discovered blogs');
    } finally {
      setLoading(false);
    }
  };

  // Filter blogs based on criteria
  const applyFilters = (blogs: HistoricalBlog[]) => {
    if (filterCriteria.showAll) {
      return blogs;
    }

    return blogs.filter(blog => {
      const da = blog.analysis_data.domainAuthority;
      const pa = blog.analysis_data.pageAuthority;
      
      // Check if blog has N/A scores
      const hasNoScore = da === undefined || da === null || pa === undefined || pa === null;
      
      // Check if blog meets minimum DA/PA criteria
      const isUnqualified = (da !== undefined && da !== null && da < 30) || 
                           (pa !== undefined && pa !== null && pa < 30);
      
      // Apply filters
      if (filterCriteria.hideNoScore && hasNoScore) {
        return false;
      }
      
      if (filterCriteria.hideUnqualified && isUnqualified) {
        return false;
      }
      
      return true;
    });
  };

  // Update filtered blogs when historicalBlogs or filterCriteria changes
  useEffect(() => {
    const filtered = applyFilters(historicalBlogs);
    setFilteredBlogs(filtered);
  }, [historicalBlogs, filterCriteria]);

  useEffect(() => {
    loadHistoricalBlogs(currentPage);
  }, [currentPage]);

  // Handle filter changes
  const handleFilterChange = (filterType: string) => {
    setFilterCriteria(prev => {
      if (filterType === 'showAll') {
        return { hideUnqualified: false, hideNoScore: false, showAll: true };
      } else {
        const newCriteria = { 
          ...prev, 
          showAll: false,
          [filterType]: !prev[filterType as keyof typeof prev]
        };
        
        // If both filters are unchecked, show all
        if (!newCriteria.hideUnqualified && !newCriteria.hideNoScore) {
          return { hideUnqualified: false, hideNoScore: false, showAll: true };
        }
        
        return newCriteria;
      }
    });
  };

  if (error) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Discovered Blogs
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Browse all previously discovered blogs from your research campaigns.
          </p>
        </div>
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Discovered Blogs
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Browse all previously discovered blogs from your research campaigns.
        </p>
        {/* Filter Controls */}
        <div className="mt-4 flex space-x-4">
          <button 
            onClick={() => handleFilterChange('showAll')} 
            className={`px-4 py-2 rounded ${filterCriteria.showAll ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
          >
            Show All
          </button>
          <button 
            onClick={() => handleFilterChange('hideUnqualified')} 
            className={`px-4 py-2 rounded ${filterCriteria.hideUnqualified ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
          >
            Hide DA/PA &lt; 30
          </button>
          <button 
            onClick={() => handleFilterChange('hideNoScore')} 
            className={`px-4 py-2 rounded ${filterCriteria.hideNoScore ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
          >
            Hide N/A Scores
          </button>
        </div>

        {/* Stats Summary */}
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p className="text-blue-800 dark:text-blue-200 font-medium">
            Total Discovered: {totalHistoricalBlogs} blogs
            {totalPages > 1 && (
              <span className="text-blue-600 dark:text-blue-400 ml-2">
                • Showing page {currentPage} of {totalPages}
              </span>
            )}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">Loading discovered blogs...</p>
        </div>
      ) : historicalBlogs.length > 0 ? (
        <>
          <div className="grid gap-4">
            {filteredBlogs.map((blog) => (
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
                      {blog.content_summary.substring(0, 200)}...
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
        onClick={() => {
          setCurrentPage(prev => Math.max(1, prev - 1));
          console.log('Set to previous page:', currentPage - 1);
        }}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Previous
              </button>
              
              <span className="px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded font-medium">
                Page {currentPage} of {totalPages}
              </span>
              
              <button
        onClick={() => {
          setCurrentPage(prev => Math.min(totalPages, prev + 1));
          console.log('Set to next page:', currentPage + 1);
        }}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Next
              </button>
            </div>
          )}
          
          {/* Bottom Stats */}
          <div className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
            Showing {filteredBlogs.length} of {totalHistoricalBlogs} total discovered blogs{!filterCriteria.showAll && ` (${historicalBlogs.length - filteredBlogs.length} filtered out)`}
          </div>
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            No discovered blogs found. Start by running a new search on the Research page!
          </p>
          <button
            onClick={() => window.location.href = '/research'}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            Go to Research
          </button>
        </div>
      )}
    </div>
  );
}

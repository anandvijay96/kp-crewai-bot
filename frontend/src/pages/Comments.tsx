import { useState, useEffect } from 'react'
import { api } from '@/utils/apiClient'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

interface Comment {
  id: string
  content: string
  style: string
  quality_score: number
  engagement_potential?: number
  keyword_density?: number
  readability_score?: number
  risk_assessment?: {
    spam_likelihood: number
    brand_safety: number
    authenticity_score: number
    policy_compliance: number
  }
  blog_url?: string
  blog_title?: string
  generated_at: string
  status?: string
}

interface CommentGenerationRequest {
  blog_url: string
  style: 'engaging' | 'question' | 'insight' | 'technical'
  max_comments: number
  keywords?: string[]
  custom_instructions?: string
}

export function Comments() {
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [generationForm, setGenerationForm] = useState<CommentGenerationRequest>({
    blog_url: '',
    style: 'engaging',
    max_comments: 3,
    keywords: [],
    custom_instructions: ''
  })

  useEffect(() => {
    fetchComments()
  }, [])

  const fetchComments = async () => {
    try {
      setLoading(true)
      console.log('🔄 Fetching comments from /api/comments/...')
      const response = await api.get('/api/comments/')
      console.log('📥 Full API response:', response)
      console.log('📋 Response type:', typeof response)
      console.log('🔑 Response keys:', response ? Object.keys(response) : 'no response')
      
      // The backend returns a BaseResponse with comments at the root level
      // Check both direct array and response.comments for compatibility
      if (Array.isArray(response)) {
        setComments(response);
        console.log('✅ Set comments from direct array:', response.length, 'comments');
      } else if (response && response.comments && Array.isArray(response.comments)) {
        setComments(response.comments);
        console.log('✅ Set comments from response.comments:', response.comments.length, 'comments');
        console.log('📝 First comment preview:', response.comments[0]);
      } else if (response && response.data && Array.isArray(response.data)) {
        setComments(response.data);
        console.log('✅ Set comments from response.data:', response.data.length, 'comments');
      } else {
        console.log('❌ No comments found in response structure:', {
          isArray: Array.isArray(response),
          hasComments: response && 'comments' in response,
          commentsType: response && response.comments ? typeof response.comments : 'no comments',
          commentsIsArray: response && response.comments ? Array.isArray(response.comments) : false,
          hasData: response && 'data' in response,
          responseKeys: response ? Object.keys(response) : 'no response',
          fullResponse: response
        });
        setComments([]);
      }
      console.log('🎯 Final comments state will be set to:', comments.length, 'items');
    } catch (error) {
      console.error('❌ Failed to fetch comments:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateComments = async () => {
    try {
      setGenerating(true)
      console.log('🤖 Generating comments...', generationForm)
      const response = await api.post('/api/comments/generate', generationForm)
      console.log('🎉 Generation response:', response)
      
      if (response.success || response.message) {
        console.log('✅ Comments generated successfully:', response.message)
        console.log('🔄 Refreshing comments list...')
        await fetchComments() // Refresh the comments list
        setGenerationForm({
          blog_url: '',
          style: 'engaging',
          max_comments: 3,
          keywords: [],
          custom_instructions: ''
        })
      } else {
        console.log('⚠️ Generation response without success flag:', response)
      }
    } catch (error) {
      console.error('❌ Failed to generate comments:', error)
    } finally {
      setGenerating(false)
    }
  }

  const exportComments = () => {
    const csvContent = [
      ['Blog URL', 'Blog Title', 'Comment', 'Style', 'Quality Score', 'Generated At'],
      ...comments.map(comment => [
        comment.blog_url,
        comment.blog_title,
        comment.content.replace(/"/g, '""'), // Escape quotes for CSV
        comment.style,
        comment.quality_score.toString(),
        comment.generated_at
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `comments-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Comments
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Generate, review, and manage AI-powered comments for blog engagement.
        </p>
      </div>

      {/* Comment Generation Form */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Generate New Comments
        </h2>
        <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">Manual Entry Feature</h3>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            Enter any blog URL directly to generate AI-powered comments. No domain authority checks required.
          </p>
          <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
            Examples: Medium articles, dev.to posts, company blogs, news articles, etc.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Blog URL
            </label>
            <input
              type="url"
              value={generationForm.blog_url}
              onChange={(e) => setGenerationForm({ ...generationForm, blog_url: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="https://medium.com/@author/seo-tips or https://dev.to/user/article-title"
              required
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Enter any blog URL. We'll analyze the content and generate relevant comments.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Comment Style
            </label>
            <select
              value={generationForm.style}
              onChange={(e) => setGenerationForm({ ...generationForm, style: e.target.value as any })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="engaging">Engaging</option>
              <option value="question">Question-based</option>
              <option value="insight">Insight-driven</option>
              <option value="technical">Technical</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Number of Comments
            </label>
            <input
              type="number"
              min="1"
              max="5"
              value={generationForm.max_comments}
              onChange={(e) => setGenerationForm({ ...generationForm, max_comments: parseInt(e.target.value) || 1 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Keywords (Optional)
            </label>
            <input
              type="text"
              value={generationForm.keywords?.join(', ') || ''}
              onChange={(e) => setGenerationForm({ 
                ...generationForm, 
                keywords: e.target.value.split(',').map(k => k.trim()).filter(k => k) 
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="SEO, content marketing, digital strategy"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Comma-separated keywords to focus on in the comments
            </p>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Custom Instructions (Optional)
            </label>
            <textarea
              value={generationForm.custom_instructions}
              onChange={(e) => setGenerationForm({ ...generationForm, custom_instructions: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              rows={3}
              placeholder="e.g., 'Focus on mobile SEO aspects' or 'Include personal experience examples'"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Specific instructions to guide comment generation
            </p>
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <Button
            onClick={generateComments}
            disabled={generating || !generationForm.blog_url}
            className="bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            {generating ? 'Generating...' : 'Generate Comments'}
          </Button>
          <Button
            onClick={() => {
              console.log('Testing API directly...')
              api.get('/api/comments/').then(response => {
                console.log('Direct API test response:', response)
                console.log('Response keys:', Object.keys(response))
                console.log('Response.comments:', response.comments)
                console.log('Response.data:', response.data)
                console.log('All response properties:', {
                  success: response.success,
                  message: response.message,
                  timestamp: response.timestamp,
                  comments: response.comments,
                  total: response.total,
                  page: response.page,
                  page_size: response.page_size
                })
                alert(`API Test: Found ${response.comments?.length || 0} comments. Success: ${response.success}. Check console for full details.`)
              }).catch(error => {
                console.error('Direct API test error:', error)
                alert('API Test failed. Check console for details.')
              })
            }}
            className="bg-yellow-600 hover:bg-yellow-700 text-white"
          >
            Test API
          </Button>
        </div>
      </Card>

      {/* Comments List */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Generated Comments ({comments.length})
        </h2>
        {comments.length > 0 && (
          <Button
            onClick={exportComments}
            variant="outline"
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            Export CSV
          </Button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            Loading comments...
          </p>
        </div>
      ) : comments.length > 0 ? (
        <div className="space-y-4">
          {comments.map((comment) => (
            <Card key={comment.id} className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Comment #{comment.id.slice(0, 8)}
                  </h3>
                  {comment.blog_url && (
                    <p className="text-sm text-blue-600 dark:text-blue-400">
                      {comment.blog_url}
                    </p>
                  )}
                </div>
                <div className="text-right">
                  {comment.status && (
                    <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
                      comment.status === 'approved' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                        : comment.status === 'pending_review'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                    }`}>
                      {comment.status.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>
              
              <p className="text-gray-900 dark:text-gray-100 mb-4 leading-relaxed">
                {comment.content}
              </p>
              
              {/* Main Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
                <div>
                  <strong>Style:</strong> {comment.style}
                </div>
                <div>
                  <strong>Quality:</strong> {(comment.quality_score * 100).toFixed(1)}%
                </div>
                {comment.engagement_potential !== undefined && (
                  <div>
                    <strong>Engagement:</strong> {(comment.engagement_potential * 100).toFixed(1)}%
                  </div>
                )}
                {comment.readability_score !== undefined && (
                  <div>
                    <strong>Readability:</strong> {(comment.readability_score * 100).toFixed(1)}%
                  </div>
                )}
              </div>
              
              {/* Additional Metrics */}
              {(comment.keyword_density !== undefined || comment.risk_assessment) && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  {comment.keyword_density !== undefined && (
                    <div>
                      <strong>Keyword Density:</strong> {(comment.keyword_density * 100).toFixed(1)}%
                    </div>
                  )}
                  {comment.risk_assessment && (
                    <>
                      <div>
                        <strong>Brand Safety:</strong> {(comment.risk_assessment.brand_safety * 100).toFixed(1)}%
                      </div>
                      <div>
                        <strong>Authenticity:</strong> {(comment.risk_assessment.authenticity_score * 100).toFixed(1)}%
                      </div>
                      <div>
                        <strong>Policy Compliance:</strong> {(comment.risk_assessment.policy_compliance * 100).toFixed(1)}%
                      </div>
                    </>
                  )}
                </div>
              )}
              
              <div className="text-xs text-gray-500 dark:text-gray-400">
                <strong>Generated:</strong> {new Date(comment.generated_at).toLocaleString()}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            No comments generated yet.
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            Use the form above to generate your first AI-powered comments.
          </p>
        </Card>
      )}
    </div>
  )
}

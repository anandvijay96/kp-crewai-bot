import { useState, useEffect } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

interface Comment {
  id: string
  content: string
  style: string
  quality_score: number
  blog_url: string
  blog_title: string
  generated_at: string
  status: string
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
      const response = await fetch('/api/comments/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setComments(data.comments || [])
      }
    } catch (error) {
      console.error('Failed to fetch comments:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateComments = async () => {
    try {
      setGenerating(true)
      const response = await fetch('/api/comments/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(generationForm)
      })
      
      if (response.ok) {
        const data = await response.json()
        await fetchComments() // Refresh the comments list
        setGenerationForm({
          blog_url: '',
          style: 'engaging',
          max_comments: 3,
          keywords: [],
          custom_instructions: ''
        })
      }
    } catch (error) {
      console.error('Failed to generate comments:', error)
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
              placeholder="https://example.com/blog-post"
            />
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
              Custom Instructions (Optional)
            </label>
            <textarea
              value={generationForm.custom_instructions}
              onChange={(e) => setGenerationForm({ ...generationForm, custom_instructions: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              rows={3}
              placeholder="Any specific instructions for comment generation..."
            />
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
                    {comment.blog_title}
                  </h3>
                  <p className="text-sm text-blue-600 dark:text-blue-400">
                    {comment.blog_url}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
                    comment.status === 'approved' 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                      : comment.status === 'pending_review'
                      ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  }`}>
                    {comment.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
              <p className="text-gray-900 dark:text-gray-100 mb-4 leading-relaxed">
                {comment.content}
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
                <div>
                  <strong>Style:</strong> {comment.style}
                </div>
                <div>
                  <strong>Quality:</strong> {(comment.quality_score * 100).toFixed(1)}%
                </div>
                <div className="col-span-2">
                  <strong>Generated:</strong> {new Date(comment.generated_at).toLocaleString()}
                </div>
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

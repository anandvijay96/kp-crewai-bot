import { useState, useEffect } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

interface AnalyticsData {
  period: string
  summary: {
    total_comments_generated: number
    approved_comments: number
    pending_review: number
    rejected_comments: number
    average_quality_score: number
    total_cost: number
  }
  style_distribution: {
    engaging: number
    question: number
    insight: number
    technical: number
  }
  quality_metrics: {
    excellent: number
    good: number
    average: number
    poor: number
  }
  performance_trends: {
    daily_generation: number[]
    quality_trend: number[]
    approval_rate: number[]
  }
  cost_analysis: {
    average_cost_per_comment: number
    cost_by_style: {
      engaging: number
      question: number
      insight: number
      technical: number
    }
    monthly_projection: number
  }
  top_performing_blogs: Array<{
    url: string
    comments: number
    avg_quality: number
  }>
}

export function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    fetchAnalytics()
  }, [days])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/comments/analytics/overview?days=${days}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data.analytics)
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportAnalytics = () => {
    if (!analytics) return
    
    const analyticsData = {
      period: analytics.period,
      summary: analytics.summary,
      style_distribution: analytics.style_distribution,
      quality_metrics: analytics.quality_metrics,
      cost_analysis: analytics.cost_analysis,
      top_performing_blogs: analytics.top_performing_blogs
    }
    
    const blob = new Blob([JSON.stringify(analyticsData, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analytics-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Analytics
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Track performance metrics and campaign insights.
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          {analytics && (
            <Button
              onClick={exportAnalytics}
              variant="outline"
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Export Data
            </Button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            Loading analytics...
          </p>
        </div>
      ) : analytics ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Comments Generated
              </h3>
              <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                {analytics.summary.total_comments_generated.toLocaleString()}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {analytics.period}
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Approval Rate
              </h3>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                {((analytics.summary.approved_comments / analytics.summary.total_comments_generated) * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {analytics.summary.approved_comments} approved
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Average Quality
              </h3>
              <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                {(analytics.summary.average_quality_score * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Quality score
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Total Cost
              </h3>
              <p className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                ${analytics.summary.total_cost.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Avg: ${analytics.cost_analysis.average_cost_per_comment.toFixed(3)}/comment
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Pending Review
              </h3>
              <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
                {analytics.summary.pending_review}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Need attention
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Monthly Projection
              </h3>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                ${analytics.cost_analysis.monthly_projection.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Estimated cost
              </p>
            </Card>
          </div>

          {/* Style Distribution */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Comment Style Distribution
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(analytics.style_distribution).map(([style, count]) => (
                <div key={style} className="text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {count}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                    {style}
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500">
                    ${analytics.cost_analysis.cost_by_style[style as keyof typeof analytics.cost_analysis.cost_by_style].toFixed(3)}/comment
                  </p>
                </div>
              ))}
            </div>
          </Card>

          {/* Quality Metrics */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Quality Distribution
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {analytics.quality_metrics.excellent}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Excellent (90-100%)
                </p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {analytics.quality_metrics.good}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Good (70-89%)
                </p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {analytics.quality_metrics.average}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Average (50-69%)
                </p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {analytics.quality_metrics.poor}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Poor (&lt;50%)
                </p>
              </div>
            </div>
          </Card>

          {/* Top Performing Blogs */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Top Performing Blogs
            </h3>
            <div className="space-y-3">
              {analytics.top_performing_blogs.map((blog, index) => (
                <div key={blog.url} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      #{index + 1} {blog.url}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">
                      {blog.comments} comments
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Avg quality: {(blog.avg_quality * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      ) : (
        <Card className="p-12 text-center">
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            No analytics data available.
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            Generate some comments first to see analytics.
          </p>
        </Card>
      )}
    </div>
  )
}

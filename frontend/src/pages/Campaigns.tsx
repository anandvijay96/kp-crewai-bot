import { Plus, Play, Pause, Settings } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

const mockCampaigns = [
  {
    id: '1',
    name: 'Tech Blog Outreach Q1',
    description: 'Targeting technology blogs for Q1 2024 outreach',
    status: 'active' as const,
    keywords: ['AI', 'machine learning', 'technology', 'innovation'],
    totalBlogs: 245,
    commentsGenerated: 89,
    commentsPosted: 67,
    successRate: 85.2,
    createdAt: '2024-01-15',
  },
  {
    id: '2',
    name: 'SaaS Content Marketing',
    description: 'Focus on SaaS and startup blogs for lead generation',
    status: 'active' as const,
    keywords: ['SaaS', 'startup', 'business', 'growth'],
    totalBlogs: 189,
    commentsGenerated: 76,
    commentsPosted: 58,
    successRate: 78.4,
    createdAt: '2024-01-10',
  },
  {
    id: '3',
    name: 'AI/ML Industry Blogs',
    description: 'Establishing thought leadership in AI/ML space',
    status: 'paused' as const,
    keywords: ['artificial intelligence', 'deep learning', 'neural networks'],
    totalBlogs: 156,
    commentsGenerated: 45,
    commentsPosted: 32,
    successRate: 71.1,
    createdAt: '2024-01-05',
  },
]

export function Campaigns() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Campaigns
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage your SEO blog commenting campaigns and track their performance.
          </p>
        </div>
        
        <Button leftIcon={<Plus className="h-4 w-4" />}>
          New Campaign
        </Button>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {mockCampaigns.map((campaign) => (
          <Card key={campaign.id} hover>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">{campaign.name}</CardTitle>
                  <CardDescription className="mt-1">
                    {campaign.description}
                  </CardDescription>
                </div>
                <span
                  className={`px-2 py-1 text-xs rounded-full ${
                    campaign.status === 'active'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                      : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                  }`}
                >
                  {campaign.status}
                </span>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-4">
                {/* Keywords */}
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                    Keywords
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {campaign.keywords.slice(0, 3).map((keyword) => (
                      <span
                        key={keyword}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                    {campaign.keywords.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 text-xs rounded">
                        +{campaign.keywords.length - 3} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {campaign.totalBlogs}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Total Blogs
                    </p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {campaign.commentsPosted}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Comments Posted
                    </p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {campaign.successRate}%
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Success Rate
                    </p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {campaign.commentsGenerated}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Generated
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    leftIcon={
                      campaign.status === 'active' ? (
                        <Pause className="h-3 w-3" />
                      ) : (
                        <Play className="h-3 w-3" />
                      )
                    }
                  >
                    {campaign.status === 'active' ? 'Pause' : 'Resume'}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<Settings className="h-3 w-3" />}
                  >
                    Settings
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

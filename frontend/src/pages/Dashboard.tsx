import { Activity, TrendingUp, MessageSquare, Target } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

// Mock data for demonstration
const stats = [
  {
    title: 'Active Campaigns',
    value: '12',
    change: '+2 from last month',
    icon: Target,
    color: 'text-blue-600',
  },
  {
    title: 'Blogs Discovered',
    value: '2,847',
    change: '+15% from last week',
    icon: Activity,
    color: 'text-green-600',
  },
  {
    title: 'Comments Generated',
    value: '1,234',
    change: '+8% from last week',
    icon: MessageSquare,
    color: 'text-purple-600',
  },
  {
    title: 'Success Rate',
    value: '87.5%',
    change: '+2.3% from last month',
    icon: TrendingUp,
    color: 'text-orange-600',
  },
]

export function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Welcome back! Here's what's happening with your SEO campaigns.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title} hover>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stat.value}
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Campaigns</CardTitle>
            <CardDescription>
              Your most recently created or modified campaigns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: 'Tech Blog Outreach Q1', status: 'Active', blogs: 245 },
                { name: 'SaaS Content Marketing', status: 'Active', blogs: 189 },
                { name: 'AI/ML Industry Blogs', status: 'Paused', blogs: 156 },
              ].map((campaign) => (
                <div key={campaign.name} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {campaign.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {campaign.blogs} blogs discovered
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      campaign.status === 'Active'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                    }`}
                  >
                    {campaign.status}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Performing Blogs</CardTitle>
            <CardDescription>
              Blogs with the highest engagement and success rates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { 
                  title: 'The Future of AI in Marketing',
                  domain: 'techcrunch.com',
                  score: 95,
                  comments: 3
                },
                { 
                  title: 'Building Scalable SaaS Products',
                  domain: 'medium.com',
                  score: 92,
                  comments: 2
                },
                { 
                  title: 'Machine Learning Best Practices',
                  domain: 'towardsdatascience.com',
                  score: 89,
                  comments: 1
                },
              ].map((blog, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 dark:text-white truncate">
                      {blog.title}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {blog.domain} • {blog.comments} comments
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {blog.score}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Quality
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

import { Activity, TrendingUp, MessageSquare, Target } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { useNavigate } from 'react-router-dom'

import { useState, useEffect } from 'react';
import { api, ApiResponse } from '@/utils/apiClient';

const fetchDashboardData = async (): Promise<DashboardData> => {
  // Try public request first (no authentication required)
  try {
    const response: ApiResponse<DashboardData> = await api.public('/api/dashboard/data');
    if (response.success && response.data) {
      return response.data;
    } else {
      throw new Error(response.message);
    }
  } catch (error) {
    // If public request fails, try authenticated request
    console.warn('Public dashboard request failed, trying authenticated request:', error);
    const response: ApiResponse<DashboardData> = await api.get('/api/dashboard/data');
    if (response.success && response.data) {
      return response.data;
    } else {
      throw new Error(response.message);
    }
  }
};

interface DashboardData {
  activeCampaigns: number;
  blogsDiscovered: number;
  commentsGenerated: number;
  successRate: number;
  recentCampaigns: Array<{ name: string; status: string; blogs: number }>;
  topBlogs: Array<{ title: string; domain: string; score: number; comments: number }>;
}

export function Dashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData()
      .then(setData)
      .catch((error) => {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data');
      });
  }, []);

  if (error) {
    return <div className="text-red-600">{error}</div>;
  }

  if (!data) {
    return <div className="text-gray-600">Loading...</div>;
  }

  const stats = [
    {
      title: 'Active Campaigns',
      value: data.activeCampaigns,
      change: '+2 from last month', // TODO: Calculate from historical data
      icon: Target,
      color: 'text-blue-600',
      route: '/campaigns',
    },
    {
      title: 'Blogs Discovered',
      value: data.blogsDiscovered,
      change: '+15% from last week', // TODO: Calculate from historical data
      icon: Activity,
      color: 'text-green-600',
      route: '/discovered-blogs',
    },
    {
      title: 'Comments Generated',
      value: data.commentsGenerated,
      change: '+8% from last week', // TODO: Calculate from historical data
      icon: MessageSquare,
      color: 'text-purple-600',
      route: '/comments',
    },
    {
      title: 'Success Rate',
      value: `${data.successRate}%`,
      change: '+2.3% from last month', // TODO: Calculate from historical data
      icon: TrendingUp,
      color: 'text-orange-600',
      route: '/analytics',
    },
  ];

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
            <Card 
              key={stat.title} 
              hover 
              onClick={() => navigate(stat.route)}
              className="cursor-pointer transition-transform hover:scale-105"
            >
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
{data.recentCampaigns.map((campaign) => (
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
{data.topBlogs.map((blog) => (
  <div key={blog.title} className="flex items-center justify-between">
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

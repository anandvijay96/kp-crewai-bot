import { useState } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { UserSettings } from '../types'

const mockUserSettings: UserSettings = {
  profile: {
    name: 'John Doe',
    email: 'john.doe@example.com',
    company: 'KloudPortal'
  },
  api_keys: {
    vertex_ai: 'AIzaSy...abc123',
    serp_api: 'serpapi_key_456',
    custom_scraping: 'scraping_key_789'
  },
  default_author_personas: [
    {
      id: '1',
      name: 'SEO Expert',
      email: 'expert@kloudportal.com',
      website: 'kloudportal.com',
      expertise_area: 'SEO & Digital Marketing',
      is_default: true
    },
    {
      id: '2',
      name: 'Tech Consultant',
      email: 'tech@kloudportal.com',
      website: 'kloudportal.com',
      expertise_area: 'Web Development',
      is_default: false
    }
  ],
  notification_preferences: {
    email_notifications: true,
    campaign_completion: true,
    error_alerts: true,
    daily_summary: false
  },
  posting_settings: {
    default_delay: 60,
    max_posts_per_day: 10,
    respect_robots_txt: true,
    user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  }
}

export function Settings() {
  const [settings, setSettings] = useState<UserSettings>(mockUserSettings)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState<'profile' | 'api' | 'personas' | 'notifications' | 'posting'>('profile')

  const saveSettings = async () => {
    try {
      setSaving(true)
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log('Settings saved:', settings)
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }

  const updateProfile = (field: keyof UserSettings['profile'], value: string) => {
    setSettings(prev => ({
      ...prev,
      profile: {
        ...prev.profile,
        [field]: value
      }
    }))
  }

  const updateApiKey = (field: keyof UserSettings['api_keys'], value: string) => {
    setSettings(prev => ({
      ...prev,
      api_keys: {
        ...prev.api_keys,
        [field]: value
      }
    }))
  }

  const updateNotification = (field: keyof UserSettings['notification_preferences'], value: boolean) => {
    setSettings(prev => ({
      ...prev,
      notification_preferences: {
        ...prev.notification_preferences,
        [field]: value
      }
    }))
  }

  const updatePostingSetting = (field: keyof UserSettings['posting_settings'], value: any) => {
    setSettings(prev => ({
      ...prev,
      posting_settings: {
        ...prev.posting_settings,
        [field]: value
      }
    }))
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Settings
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Configure your account, API keys, and application preferences.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'profile', name: 'Profile' },
            { id: 'api', name: 'API Keys' },
            { id: 'personas', name: 'Author Personas' },
            { id: 'notifications', name: 'Notifications' },
            { id: 'posting', name: 'Posting Settings' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            User Profile
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={settings.profile.name}
                onChange={(e) => updateProfile('name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={settings.profile.email}
                onChange={(e) => updateProfile('email', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Company (Optional)
              </label>
              <input
                type="text"
                value={settings.profile.company || ''}
                onChange={(e) => updateProfile('company', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'api' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            API Keys
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Google Vertex AI API Key
              </label>
              <input
                type="password"
                value={settings.api_keys.vertex_ai || ''}
                onChange={(e) => updateApiKey('vertex_ai', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Enter your Vertex AI API key"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Used for AI-powered comment generation
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                SERP API Key (Optional)
              </label>
              <input
                type="password"
                value={settings.api_keys.serp_api || ''}
                onChange={(e) => updateApiKey('serp_api', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Enter your SERP API key"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Used for enhanced search capabilities
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Custom Scraping API Key (Optional)
              </label>
              <input
                type="password"
                value={settings.api_keys.custom_scraping || ''}
                onChange={(e) => updateApiKey('custom_scraping', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Enter your custom scraping API key"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Used for premium scraping services
              </p>
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'personas' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Author Personas
          </h2>
          <div className="space-y-4">
            {settings.default_author_personas.map((persona) => (
              <div key={persona.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {persona.name}
                    {persona.is_default && (
                      <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300 rounded">
                        Default
                      </span>
                    )}
                  </h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Email: {persona.email}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Website: {persona.website}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Expertise: {persona.expertise_area}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {activeTab === 'notifications' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Notification Preferences
          </h2>
          <div className="space-y-4">
            {[
              { key: 'email_notifications', label: 'Email Notifications', description: 'Receive general notifications via email' },
              { key: 'campaign_completion', label: 'Campaign Completion', description: 'Get notified when campaigns finish' },
              { key: 'error_alerts', label: 'Error Alerts', description: 'Immediate alerts for system errors' },
              { key: 'daily_summary', label: 'Daily Summary', description: 'Daily performance summary emails' }
            ].map((notification) => (
              <div key={notification.key} className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                    {notification.label}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {notification.description}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notification_preferences[notification.key as keyof typeof settings.notification_preferences]}
                    onChange={(e) => updateNotification(notification.key as any, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 dark:peer-focus:ring-indigo-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-600"></div>
                </label>
              </div>
            ))}
          </div>
        </Card>
      )}

      {activeTab === 'posting' && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Posting Settings
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Default Posting Delay (seconds)
              </label>
              <input
                type="number"
                min="30"
                max="3600"
                value={settings.posting_settings.default_delay}
                onChange={(e) => updatePostingSetting('default_delay', parseInt(e.target.value) || 60)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Posts per Day
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={settings.posting_settings.max_posts_per_day}
                onChange={(e) => updatePostingSetting('max_posts_per_day', parseInt(e.target.value) || 10)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                User Agent String
              </label>
              <input
                type="text"
                value={settings.posting_settings.user_agent}
                onChange={(e) => updatePostingSetting('user_agent', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
            <div className="md:col-span-2">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="respect-robots"
                  checked={settings.posting_settings.respect_robots_txt}
                  onChange={(e) => updatePostingSetting('respect_robots_txt', e.target.checked)}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="respect-robots" className="ml-2 block text-sm text-gray-900 dark:text-white">
                  Respect robots.txt files
                </label>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Follow website robots.txt directives when posting comments
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={saveSettings}
          disabled={saving}
          className="bg-indigo-600 hover:bg-indigo-700 text-white"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  )
}

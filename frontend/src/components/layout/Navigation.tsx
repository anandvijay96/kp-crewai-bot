import { useLocation } from 'react-router-dom'
import { 
  Home, 
  Zap, 
  Search, 
  Database,
  MessageSquare, 
  BarChart3, 
  Settings as SettingsIcon 
} from 'lucide-react'
import { cn } from '@/utils/cn'
import { Button } from '@/components/ui/Button'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Campaigns', href: '/campaigns', icon: Zap },
  { name: 'Blog Research', href: '/research', icon: Search },
  { name: 'Discovered Blogs', href: '/discovered-blogs', icon: Database },
  { name: 'Comments', href: '/comments', icon: MessageSquare },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: SettingsIcon },
]

export function Navigation() {
  const location = useLocation()

  return (
    <nav className="bg-gray-50 border-b border-gray-200 dark:bg-gray-900 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap gap-2 p-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon

            return (
              <Button
                key={item.name}
                variant={isActive ? 'primary' : 'ghost'}
                size="sm"
                className={cn(
                  'flex items-center gap-2 px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-800'
                )}
                onClick={() => {
                  window.location.href = item.href
                }}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{item.name}</span>
              </Button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}

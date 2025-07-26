import { Bell, Moon, Sun, User } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useTheme } from '@/hooks/useTheme'

export function Header() {
  const { theme, setTheme, isDark } = useTheme()

  const toggleTheme = () => {
    // Cycle through: light -> dark -> system -> light
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0 flex items-center">
              <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">KP</span>
              </div>
              <div className="ml-3">
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                  KloudPortal
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  SEO Automation Platform
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2">
            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="h-9 w-9 p-0"
            >
              {isDark ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            {/* Notifications */}
            <Button
              variant="ghost"
              size="sm"
              className="h-9 w-9 p-0 relative"
            >
              <Bell className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs flex items-center justify-center text-white">
                3
              </span>
            </Button>

            {/* User Menu */}
            <Button
              variant="ghost"
              size="sm"
              className="h-9 w-9 p-0"
            >
              <User className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}

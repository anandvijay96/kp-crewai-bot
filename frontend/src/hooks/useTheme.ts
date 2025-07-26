import { useState, useEffect } from 'react'

type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    // Check if we're on the client side
    if (typeof window !== 'undefined') {
      const storedTheme = localStorage.getItem('theme') as Theme
      if (storedTheme) {
        return storedTheme
      }
    }
    return 'system'
  })

  useEffect(() => {
    const root = window.document.documentElement
    
    // Remove existing theme classes
    root.classList.remove('light', 'dark')

    let effectiveTheme: 'light' | 'dark'

    if (theme === 'system') {
      // Use system preference
      effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
    } else {
      effectiveTheme = theme
    }

    // Apply the theme
    root.classList.add(effectiveTheme)
    
    // Store in localStorage
    localStorage.setItem('theme', theme)
  }, [theme])

  // Listen for system theme changes when using 'system'
  useEffect(() => {
    if (theme !== 'system') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = () => {
      const root = window.document.documentElement
      root.classList.remove('light', 'dark')
      root.classList.add(mediaQuery.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const setThemeMode = (newTheme: Theme) => {
    setTheme(newTheme)
  }

  const isDark = () => {
    if (theme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return theme === 'dark'
  }

  return { 
    theme, 
    setTheme: setThemeMode, 
    isDark: isDark(),
    systemTheme: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
}

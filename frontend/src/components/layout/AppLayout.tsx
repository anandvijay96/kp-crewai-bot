import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { Navigation } from './Navigation'
import { RouteTransition } from './RouteTransition'

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <RouteTransition>
          <Outlet />
        </RouteTransition>
      </main>
    </div>
  )
}

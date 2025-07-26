// Simple debug version to test React rendering
import { BrowserRouter as Router } from 'react-router-dom'

export function App() {
  console.log('App component is rendering...')
  
  return (
    <Router>
      <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
        <h1 style={{ color: '#333', fontSize: '24px', marginBottom: '20px' }}>
          🚀 KloudPortal SEO Bot - Debug Mode
        </h1>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h2 style={{ color: '#666', fontSize: '18px' }}>Debug Information:</h2>
          <ul style={{ lineHeight: '1.6' }}>
            <li>✅ React is working</li>
            <li>✅ Router is working</li>
            <li>✅ Basic styling is working</li>
            <li>Environment: {import.meta.env.DEV ? 'Development' : 'Production'}</li>
            <li>API URL: {import.meta.env.VITE_API_URL || 'http://localhost:8000'}</li>
          </ul>
        </div>
        
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e7f3ff', borderRadius: '8px' }}>
          <h3 style={{ color: '#0066cc', fontSize: '16px', marginBottom: '10px' }}>Next Steps:</h3>
          <p style={{ color: '#333', fontSize: '14px' }}>
            If you can see this page, React is working correctly. We can now proceed with the authentication integration.
          </p>
        </div>

        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fff3cd', borderRadius: '8px' }}>
          <h3 style={{ color: '#856404', fontSize: '16px', marginBottom: '10px' }}>Test Authentication:</h3>
          <button 
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer' 
            }}
            onClick={() => {
              fetch('http://localhost:8000/health')
                .then(res => res.json())
                .then(data => {
                  alert('Backend connection successful! Response: ' + JSON.stringify(data, null, 2))
                })
                .catch(err => {
                  alert('Backend connection failed: ' + err.message)
                })
            }}
          >
            Test Backend Connection
          </button>
        </div>
      </div>
    </Router>
  )
}

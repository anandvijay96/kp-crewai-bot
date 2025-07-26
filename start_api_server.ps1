# Start API Server in Background
# =============================
# 
# PowerShell script to start the test API server in the background for integration testing.

Write-Host "🚀 Starting KP Bot Auth Test API Server..." -ForegroundColor Green
Write-Host "📍 API will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📖 API docs at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan

# Start the server in a new PowerShell window
$process = Start-Process -FilePath "python" -ArgumentList "test_api_server.py" -WindowStyle Minimized -PassThru

Write-Host "✅ API server started with PID: $($process.Id)" -ForegroundColor Green
Write-Host "🔄 Waiting for server to be ready..." -ForegroundColor Yellow

# Wait for server to start
Start-Sleep -Seconds 5

# Test if server is running
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 10
    Write-Host "✅ Server is ready!" -ForegroundColor Green
    Write-Host "   Service: $($response.service)" -ForegroundColor Gray
    Write-Host "   Status: $($response.status)" -ForegroundColor Gray
    
    Write-Host "`n📋 Test credentials:" -ForegroundColor Cyan
    Write-Host "   - test@example.com / password123 (user)" -ForegroundColor Gray
    Write-Host "   - admin@example.com / admin123 (admin)" -ForegroundColor Gray
    
    Write-Host "`n🧪 Run integration tests with:" -ForegroundColor Yellow
    Write-Host "   python test_frontend_integration.py" -ForegroundColor White
    
    Write-Host "`n⏹️ To stop the server, run:" -ForegroundColor Yellow
    Write-Host "   Stop-Process -Id $($process.Id)" -ForegroundColor White
    
    # Return process ID for reference
    return $process.Id
    
} catch {
    Write-Host "❌ Server failed to start or respond" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Clean up if server didn't start properly
    if ($process -and !$process.HasExited) {
        Stop-Process -Id $process.Id -Force
        Write-Host "🧹 Cleaned up failed server process" -ForegroundColor Yellow
    }
    
    return $null
}

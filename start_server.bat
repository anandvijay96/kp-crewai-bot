@echo off
echo Starting KP Bot Auth Test API Server...
echo API will be available at: http://127.0.0.1:8000
echo API docs at: http://127.0.0.1:8000/docs
echo.
echo Test credentials:
echo   - test@example.com / password123 (user)
echo   - admin@example.com / admin123 (admin)
echo.
echo Starting server...
python test_api_server.py

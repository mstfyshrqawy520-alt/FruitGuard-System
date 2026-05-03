@echo off
echo Building Fruite AI - Production APK...
echo ---------------------------------------
echo.

:: You can pass the API_URL as an argument or it defaults to the Render URL
set "API_URL=%~1"
if "%API_URL%"=="" set "API_URL=https://fruit-ai-api.onrender.com"

echo Using API URL: %API_URL%

call flutter build apk --release --dart-define=API_URL=%API_URL%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] APK Build Failed!
    exit /b %errorlevel%
)

echo.
echo [SUCCESS] Build completed.
echo APK Location: build\app\outputs\flutter-apk\app-release.apk
pause

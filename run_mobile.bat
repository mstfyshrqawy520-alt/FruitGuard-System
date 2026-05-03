@echo off
echo ====================================
echo     Starting Mobile (Auto-Detect)...
echo ====================================
cd frontend

echo Fetching Flutter dependencies...
call flutter pub get

echo Launching app...
flutter run

pause

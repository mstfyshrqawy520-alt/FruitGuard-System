@echo off
setlocal enabledelayedexpansion

:: Find the real cmake.exe (skip this bat file)
set "REAL_CMAKE="
for /f "delims=" %%I in ('where cmake 2^>nul') do (
    echo %%I | findstr /i /v "cmake.bat" >nul
    if !errorlevel! equ 0 (
        set "REAL_CMAKE=%%I"
        goto :found
    )
)
:found

if "%REAL_CMAKE%"=="" (
    echo [ERROR] Real CMake not found!
    exit /b 1
)

:: Replace the hardcoded VS 2019 generator from Flutter with the installed VS 2026
set "ARGS="
:loop
if "%~1"=="" goto :execute
set "ARG=%~1"
if /i "!ARG!"=="Visual Studio 16 2019" (
    set "ARGS=!ARGS! "Visual Studio 18 2026""
) else if /i "!ARG!"=="Visual Studio 17 2022" (
    set "ARGS=!ARGS! "Visual Studio 18 2026""
) else (
    :: Safely quote arguments containing spaces
    echo !ARG! | find " " >nul
    if !errorlevel! equ 0 (
        set "ARGS=!ARGS! "!ARG!""
    ) else (
        set "ARGS=!ARGS! !ARG!"
    )
)
shift
goto :loop

:execute
echo [CMake Interceptor] Calling real CMake with fixed generator: !ARGS!
"%REAL_CMAKE%" !ARGS!
exit /b !errorlevel!

@echo off
echo ========================================================
echo Pushing SatyaNet (VakyaGuard) to GitHub: vyshu
echo Repository: https://github.com/vyshnavi0171-dotcom/vyshu.git
echo ========================================================
echo.

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo.
    echo Please install Git for Windows by either:
    echo 1. Downloading from https://git-scm.com/download/win
    echo 2. Running in PowerShell: winget install --id Git.Git -e --source winget
    echo.
    echo After installing, reopen this script.
    pause
    exit /b 1
)

echo [1/5] Initializing Git repository...
git init

echo [2/5] Adding all files to staging...
git add .

echo [3/5] Creating initial commit...
git commit -m "feat: SatyaNet (VakyaGuard) Multi-Modal Misinformation & Audio Deepfake Detector MVP"

echo [4/5] Setting main branch and remote origin...
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/vyshnavi0171-dotcom/vyshu.git

echo [5/5] Pushing to GitHub...
echo (A GitHub login window may appear to authenticate your account)
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo SUCCESS! Your project has been pushed to:
    echo https://github.com/vyshnavi0171-dotcom/vyshu
    echo ========================================================
) else (
    echo.
    echo [FAILED] Push failed. If authentication failed, ensure you are signed into GitHub.
)

pause

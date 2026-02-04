@echo off
REM Baby Monitor Release Creator for Windows
echo 🚀 Baby Monitor Release Creator
echo ===============================

REM Check if GitHub CLI is available
gh --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ GitHub CLI found

    REM Check if authenticated
    gh auth status >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ GitHub CLI authenticated

        REM Get version
        for /f %%i in ('git rev-list --count HEAD') do set VERSION=%%i
        set TAG=v1.1.%VERSION%

        echo 📋 Release Info:
        echo    Version: %TAG%
        echo    Repository: elgodox/baby-monitor-audio

        REM Create release
        echo 🔄 Creating release...
        gh release create "%TAG%" ^
            --repo "elgodox/baby-monitor-audio" ^
            --title "Baby Monitor Audio %TAG%" ^
            --notes-file "RELEASE_NOTES.md" ^
            --latest ^
            "baby-monitor-audio-%TAG%.zip"

        if %errorlevel% equ 0 (
            echo 🎉 Release created successfully!
            echo 📁 https://github.com/elgodox/baby-monitor-audio/releases/tag/%TAG%
        ) else (
            echo ❌ Failed to create release
        )

    ) else (
        echo ❌ GitHub CLI not authenticated
        echo    Run: gh auth login
    )

) else (
    echo ❌ GitHub CLI not found
    echo    Install from: https://cli.github.com/
    echo.
    echo 📋 Manual Release Creation:
    echo 1. Go to: https://github.com/elgodox/baby-monitor-audio/releases/new

    for /f %%i in ('git rev-list --count HEAD') do echo 2. Tag: v1.1.%%i
    for /f %%i in ('git rev-list --count HEAD') do echo 3. Title: Baby Monitor Audio v1.1.%%i
    echo 4. Copy content from RELEASE_NOTES.md
    for /f %%i in ('git rev-list --count HEAD') do echo 5. Upload: baby-monitor-audio-v1.1.%%i.zip
    echo 6. Click 'Publish release'
)

echo.
pause
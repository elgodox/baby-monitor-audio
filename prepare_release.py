#!/usr/bin/env python3
"""
Simple Release Creator for Baby Monitor
Creates a portable installer and prepares release notes
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_portable_installer():
    """Create a portable ZIP installer"""

    # Get version from git
    try:
        import subprocess
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                              capture_output=True, text=True, check=True)
        commit_count = result.stdout.strip()
        version = f"v1.1.{commit_count}"
    except:
        version = f"v1.1.{datetime.now().strftime('%Y%m%d')}"

    installer_name = f"baby-monitor-audio-{version}"
    zip_name = f"{installer_name}.zip"

    print(f"🔄 Creando installer portable: {zip_name}")

    # Create temp directory
    if os.path.exists(installer_name):
        shutil.rmtree(installer_name)
    os.makedirs(installer_name)

    # Files to include
    files_to_include = [
        'BabyMonitor.pyw',
        'README.md',
        'requirements.txt',
        'LICENSE',
        'create_release.py'
    ]

    for file in files_to_include:
        if os.path.exists(file):
            shutil.copy2(file, installer_name)
            print(f"  ✅ Copiado: {file}")

    # Create launcher scripts
    create_launcher_scripts(installer_name, version)

    # Create ZIP
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(installer_name):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, installer_name)
                zipf.write(file_path, arc_name)

    # Cleanup
    shutil.rmtree(installer_name)

    print(f"✅ Installer creado: {zip_name} ({os.path.getsize(zip_name)} bytes)")

    return zip_name, version

def create_launcher_scripts(installer_name, version):
    """Create launcher scripts for different platforms"""

    # Windows batch file
    batch_content = f'''@echo off
REM Baby Monitor Audio - Portable Launcher
echo.
echo ===========================================
echo   👶 Baby Monitor Audio {version}
echo   Portable Edition
echo ===========================================
echo.

echo 📦 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python 3.6 or higher from:
    echo https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

echo 📦 Installing/Checking dependencies...
echo This may take a moment...
echo.

pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    echo.
    echo Try running: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

echo 🚀 Starting Baby Monitor...
echo.
echo Close this window to stop the monitor
echo.

python BabyMonitor.pyw

echo.
echo 👶 Baby Monitor stopped
pause
'''

    with open(f"{installer_name}/START_Windows.bat", 'w', encoding='utf-8') as f:
        f.write(batch_content)

    # Linux/macOS shell script
    shell_content = f'''#!/bin/bash
# Baby Monitor Audio - Portable Launcher
echo ""
echo "==========================================="
echo "  👶 Baby Monitor Audio {version}"
echo "  Portable Edition"
echo "==========================================="
echo ""

echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ ERROR: Python not found!"
    echo ""
    echo "Please install Python 3.6 or higher"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    echo ""
    read -p "Press Enter to exit"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✅ Python found ($PYTHON_CMD)"
echo ""

echo "📦 Installing/Checking dependencies..."
echo "This may take a moment..."
echo ""

$PYTHON_CMD -m pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to install dependencies"
    echo ""
    echo "Try running: $PYTHON_CMD -m pip install -r requirements.txt"
    echo ""
    read -p "Press Enter to exit"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

echo "🚀 Starting Baby Monitor..."
echo "Close this terminal to stop the monitor"
echo ""

$PYTHON_CMD BabyMonitor.pyw

echo ""
echo "👶 Baby Monitor stopped"
read -p "Press Enter to exit"
'''

    with open(f"{installer_name}/start_linux_macos.sh", 'w', encoding='utf-8') as f:
        f.write(shell_content)

    # Make shell script executable
    os.chmod(f"{installer_name}/start_linux_macos.sh", 0o755)

def create_release_notes(version, zip_name):
    """Create release notes"""

    release_notes = f'''# Baby Monitor Audio {version}

## 🚀 What's New in This Release

### ✨ New Features
- **🎤 Real-time Audio Streaming** - Hear your baby with crystal clear audio
- **📹 Multi-Camera Support** - Automatically detect and switch between cameras
- **🔄 Dynamic Device Selection** - Change cameras/audio devices on the fly
- **⚡ Smart Fallbacks** - Works perfectly even with missing devices
- **🌙 Modern UI** - Beautiful dark interface with status indicators

### 📦 Portable Installer
- **One-click setup** - No complex installation required
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Self-contained** - Includes all dependencies
- **Offline ready** - Works without internet after setup

## 🛠️ Installation

### Option 1: Portable ZIP (Recommended)
1. Download `{zip_name}`
2. Extract the ZIP file anywhere
3. **Windows**: Double-click `START_Windows.bat`
4. **macOS/Linux**: Run `./start_linux_macos.sh`

### Option 2: From Source
```bash
git clone https://github.com/elgodox/baby-monitor-audio.git
cd baby-monitor-audio
pip install -r requirements.txt
python BabyMonitor.pyw
```

## 🎯 How to Use

1. **Launch the app** using the provided script
2. **Select your camera** from the dropdown menu
3. **Click START** to begin monitoring
4. **Scan QR code** or share the secure link
5. **Audio streams automatically** when available

## 🔧 System Requirements

- **Python 3.6+**
- **Webcam** (built-in or external)
- **Microphone** (recommended for audio)
- **WiFi network** for remote access

## 📱 Supported Devices

- 📺 **Computers**: Windows, macOS, Linux
- 📱 **Phones**: iOS Safari, Android Chrome
- 📲 **Tablets**: iPad, Android tablets
- 🌐 **Any device** with a web browser

## 🔒 Security Features

- **Local-only streaming** - No cloud upload
- **Secure tokens** - Unique access codes
- **Private network** - Only devices on your WiFi
- **No data collection** - 100% private

## 🐛 Troubleshooting

### Audio Not Working
- Check microphone permissions in system settings
- Try different audio devices
- App works fine with video-only mode

### Camera Not Detected
- Ensure camera drivers are installed
- Try different USB ports
- Close other camera apps

### Connection Issues
- Ensure devices are on the same WiFi network
- Check firewall settings
- Try different browsers

## 📋 Changelog

### {version}
- Added real-time audio streaming
- Implemented multi-camera detection
- Enhanced UI with status indicators
- Created portable installer
- Improved error handling
- Added cross-platform support

## 🙏 Acknowledgments

- **Forked from**: [Recentlystarted/baby-monitor](https://github.com/Recentlystarted/baby-monitor)
- **Original inspiration**: CodeWithHarry tutorials
- **Audio enhancements**: sounddevice library integration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/elgodox/baby-monitor-audio/issues)
- **Discussions**: [GitHub Discussions](https://github.com/elgodox/baby-monitor-audio/discussions)

---

**Made with ❤️ for parents everywhere**
'''

    with open('RELEASE_NOTES.md', 'w', encoding='utf-8') as f:
        f.write(release_notes)

    print("✅ Release notes creadas: RELEASE_NOTES.md")

def main():
    print("🚀 Baby Monitor - Release Preparer")
    print("=" * 40)

    # Create portable installer
    zip_name, version = create_portable_installer()

    # Create release notes
    create_release_notes(version, zip_name)

    print("\n🎉 ¡Preparación de release completada!")
    print("📦 Installer: {}".format(zip_name))
    print("📝 Release Notes: RELEASE_NOTES.md")
    print("\n📋 Próximos pasos:")
    print("1. Ve a https://github.com/elgodox/baby-monitor-audio/releases")
    print("2. Click 'Create a new release'")
    print("3. Tag version: {}".format(version))
    print("4. Title: Baby Monitor Audio {}".format(version))
    print("5. Copy content from RELEASE_NOTES.md")
    print("6. Upload the ZIP file as asset")
    print("7. Click 'Publish release'")
    print("\n🔗 Tu installer está listo para distribuir!")

if __name__ == "__main__":
    main()
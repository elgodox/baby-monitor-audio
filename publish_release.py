#!/usr/bin/env python3
"""
Automated Release Publisher
Opens GitHub releases page and copies release notes to clipboard
"""

import webbrowser
import subprocess
import platform
import os

def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        if platform.system() == "Windows":
            # Windows
            subprocess.run(['clip'], input=text, text=True, check=True)
        elif platform.system() == "Darwin":
            # macOS
            subprocess.run(['pbcopy'], input=text, text=True, check=True)
        else:
            # Linux
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'],
                             input=text, text=True, check=True)
            except FileNotFoundError:
                try:
                    subprocess.run(['xsel', '--clipboard', '--input'],
                                 input=text, text=True, check=True)
                except FileNotFoundError:
                    print("⚠️  No clipboard tool found. You'll need to copy manually.")
                    return False
        return True
    except Exception as e:
        print(f"⚠️  Could not copy to clipboard: {e}")
        return False

def main():
    print("🚀 Baby Monitor Release Publisher")
    print("=" * 40)

    # Get version
    try:
        result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                              capture_output=True, text=True, check=True)
        version = f"v1.1.{result.stdout.strip()}"
    except:
        version = "v1.1.0"

    print(f"📋 Version: {version}")
    print("📁 Repository: elgodox/baby-monitor-audio")

    # Read release notes
    try:
        with open('RELEASE_NOTES.md', 'r', encoding='utf-8') as f:
            release_notes = f.read()
        print("✅ Release notes loaded")
    except FileNotFoundError:
        print("❌ RELEASE_NOTES.md not found. Run prepare_release.py first")
        return

    # Copy to clipboard
    if copy_to_clipboard(release_notes):
        print("✅ Release notes copied to clipboard")
    else:
        print("ℹ️  Copy the content from RELEASE_NOTES.md manually")

    # Open GitHub releases page
    releases_url = "https://github.com/elgodox/baby-monitor-audio/releases/new"
    print(f"🔗 Opening: {releases_url}")

    try:
        webbrowser.open(releases_url)
        print("✅ Browser opened")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")
        print(f"   Please visit: {releases_url}")

    print("\n📋 Instructions:")
    print(f"1. Tag version: {version}")
    print(f"2. Title: Baby Monitor Audio {version}")
    print("3. Description: (already copied to clipboard)")
    print("4. Upload: baby-monitor-audio-{}.zip".format(version))
    print("5. Click 'Publish release'")
    print("\n🎉 Ready to publish!")

if __name__ == "__main__":
    main()
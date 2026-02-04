#!/usr/bin/env bash
# Baby Monitor Release Creator
# Automated script to create GitHub releases

echo "🚀 Baby Monitor Release Creator"
echo "==============================="

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found"

    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI authenticated"

        # Get version
        VERSION=$(git rev-list --count HEAD)
        TAG="v1.1.$VERSION"

        echo "📋 Release Info:"
        echo "   Version: $TAG"
        echo "   Repository: elgodox/baby-monitor-audio"

        # Create release
        echo "🔄 Creating release..."
        gh release create "$TAG" \
            --repo "elgodox/baby-monitor-audio" \
            --title "Baby Monitor Audio $TAG" \
            --notes-file "RELEASE_NOTES.md" \
            --latest \
            "baby-monitor-audio-$TAG.zip"

        if [ $? -eq 0 ]; then
            echo "🎉 Release created successfully!"
            echo "📁 https://github.com/elgodox/baby-monitor-audio/releases/tag/$TAG"
        else
            echo "❌ Failed to create release"
        fi

    else
        echo "❌ GitHub CLI not authenticated"
        echo "   Run: gh auth login"
    fi

else
    echo "❌ GitHub CLI not found"
    echo "   Install from: https://cli.github.com/"
    echo ""
    echo "📋 Manual Release Creation:"
    echo "1. Go to: https://github.com/elgodox/baby-monitor-audio/releases/new"
    echo "2. Tag: v1.1.$(git rev-list --count HEAD)"
    echo "3. Title: Baby Monitor Audio v1.1.X"
    echo "4. Copy content from RELEASE_NOTES.md"
    echo "5. Upload: baby-monitor-audio-v1.1.X.zip"
    echo "6. Click 'Publish release'"
fi
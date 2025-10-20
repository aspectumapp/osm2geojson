#!/bin/bash
# Test script to verify the package builds correctly

set -e  # Exit on error

echo "🧪 Testing package build..."
echo ""

# Clean old builds
echo "🧹 Cleaning old builds..."
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "📦 Building package..."
python -m build

# Check what files are included
echo ""
echo "📋 Package contents:"
tar -tzf dist/osm2geojson-*.tar.gz | head -20

# Verify JSON files are included
echo ""
echo "🔍 Checking for JSON files in package..."
if tar -tzf dist/osm2geojson-*.tar.gz | grep -q "\.json$"; then
    echo "✅ JSON files found in package"
else
    echo "❌ WARNING: No JSON files found in package!"
    exit 1
fi

# Check wheel contents
echo ""
echo "📋 Wheel contents:"
unzip -l dist/osm2geojson-*.whl | grep "\.json" || echo "⚠️  No JSON files in wheel"

echo ""
echo "✅ Build test complete!"
echo ""
echo "To test installation:"
echo "  pip install dist/osm2geojson-*.whl"

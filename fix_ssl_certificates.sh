#!/bin/bash
# Fix SSL Certificate Error on macOS

echo "🔧 Fixing SSL Certificate Issue on macOS..."
echo ""

# Method 1: Run Python's certificate installer
echo "Method 1: Running Python certificate installer..."
python3 /Applications/Python\ 3.*/Install\ Certificates.command 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Certificates installed successfully!"
else
    echo "⚠️  Certificate installer not found or failed."
    echo ""
    echo "Method 2: Installing certifi..."
    pip install --upgrade certifi
    
    echo ""
    echo "Method 3: Manual fix..."
    echo "Run this command to install certificates:"
    echo ""
    echo "sudo /Applications/Python\ 3.*/Install\ Certificates.command"
    echo ""
fi

echo ""
echo "📝 Alternative Solutions:"
echo "1. For Python 3.14 (your version):"
echo "   sudo /Applications/Python\ 3.14/Install\ Certificates.command"
echo ""
echo "2. Or install certifi and point to it:"
echo "   pip install --upgrade certifi"
echo ""
echo "3. Or temporarily for testing, use port 465 with SSL:"
echo "   EMAIL_PORT = 465"
echo "   EMAIL_USE_TLS = False"
echo "   EMAIL_USE_SSL = True"
echo ""
echo "After running this, restart your Django server."

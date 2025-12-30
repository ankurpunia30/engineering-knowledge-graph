#!/bin/bash

# Test script for Railway deployment
# Tries common URL patterns

echo "🔍 Testing Railway deployment URLs..."
echo ""

# Possible URLs based on project name
URLS=(
    "https://humorous-cooperation-production.up.railway.app"
    "https://humorous-cooperation.up.railway.app"
    "https://engineering-knowledge-graph-production.up.railway.app"
)

for URL in "${URLS[@]}"; do
    echo "Testing: $URL"
    
    # Test health endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$URL/health" 2>/dev/null)
    
    if [ "$RESPONSE" = "200" ]; then
        echo "✅ SUCCESS! Your app is live at:"
        echo "   $URL"
        echo ""
        echo "📋 Test your endpoints:"
        echo "   Health: $URL/health"
        echo "   API Docs: $URL/docs"
        echo "   Chat: $URL/api/chat"
        echo ""
        
        # Test the health endpoint
        echo "🧪 Health check response:"
        curl -s "$URL/health" | python3 -m json.tool
        echo ""
        exit 0
    else
        echo "   ❌ Not found (HTTP $RESPONSE)"
    fi
    echo ""
done

echo "⚠️  Could not find your Railway URL automatically."
echo ""
echo "📋 Manual steps:"
echo "1. Go to: https://railway.app/project/2c1f6d89-8dd3-46b4-ac7f-47ac943452d9"
echo "2. Click on your service"
echo "3. Go to Settings → Networking"
echo "4. Click 'Generate Domain' if you don't see a URL"
echo "5. Copy your URL and test with:"
echo "   curl YOUR_URL/health"

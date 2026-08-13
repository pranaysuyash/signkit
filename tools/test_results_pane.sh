#!/bin/bash
echo "=== Testing Results Pane Functionality ==="
echo ""
echo "1. Testing backend connection..."
curl -s http://127.0.0.1:8001/health | python3 -m json.tool
echo ""
echo "2. Starting desktop app (will timeout after 10 seconds)..."
if [ -x "venv/bin/activate" ]; then
  . venv/bin/activate
elif [ -x ".venv/bin/activate" ]; then
  . .venv/bin/activate
else
  echo "No local virtualenv activation script found. Expected ./venv/bin/activate or ./.venv/bin/activate."
  exit 1
fi
timeout 10s python -m desktop_app.main &
APP_PID=$!
sleep 5
echo "App process status:"
ps aux | grep "python -m desktop_app.main" | grep -v grep || echo "App not running"
kill $APP_PID 2>/dev/null
echo ""
echo "3. To manually test the results pane:"
echo "   a. Run: source venv/bin/activate && python -m desktop_app.main"
echo "   b. Upload an image"
echo "   c. Make a selection on the source image"
echo "   d. Wait for processing (watch status bar)"
echo "   e. Check if the result appears in the Result pane"
echo ""
echo "If results still don't appear, check:"
echo "- Console/terminal for error messages"
echo "- Backend logs for processing errors"
echo "- Network connectivity to http://127.0.0.1:8001"

#!/bin/bash

# SignKit Landing Page Safe Deployment Script
# This script verifies files before deploying to Cloudflare Pages

set -e

# Retained filename for compatibility. The old body below is historical and
# attempted to commit landing changes before deployment. Route all use through
# the canonical, non-mutating deployment gate instead.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/deploy_canonical_landing.sh" "$@"

echo "🚀 SignKit Landing Page Deployment"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Step 1: Verify we're on the right branch
echo "${BLUE}Step 1: Checking git branch...${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "${YELLOW}⚠ Warning: You're on branch '$CURRENT_BRANCH', not 'main'${NC}"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
else
    echo "${GREEN}✓ On main branch${NC}"
fi
echo ""

# Step 2: Check for uncommitted changes
echo "${BLUE}Step 2: Checking for uncommitted changes...${NC}"
LANDING_FILES="*.html _redirects wrangler.toml assets/ screenshots/ web/"
if ! git diff-index --quiet HEAD -- $LANDING_FILES 2>/dev/null; then
    echo "${YELLOW}⚠ You have uncommitted changes in landing page files${NC}"
    echo ""
    git status --short $LANDING_FILES 2>/dev/null || true
    echo ""
    read -p "Commit changes before deploying? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo ""
        read -p "Enter commit message: " COMMIT_MSG
        git add $LANDING_FILES
        git commit -m "$COMMIT_MSG"
        echo "${GREEN}✓ Changes committed${NC}"
    fi
else
    echo "${GREEN}✓ No uncommitted changes${NC}"
fi
echo ""

# Step 3: Run verification
echo "${BLUE}Step 3: Running pre-deployment verification...${NC}"
echo ""
if ! "$SCRIPT_DIR/verify_deployment.sh"; then
    echo ""
    echo "${RED}❌ Verification failed!${NC}"
    echo "Fix the errors above before deploying."
    exit 1
fi
echo ""

# Step 4: Show what will be deployed
echo "${BLUE}Step 4: Files to be deployed:${NC}"
cd "$PROJECT_ROOT"
echo "  Directory: $(pwd)"
echo "  HTML files: $(ls -1 *.html 2>/dev/null | wc -l)"
echo "  Key files:"
echo "    - index.html (main entry with A/B routing)"
echo "    - root.html (neo-brutalist variant)"
echo "    - buy.html (embedded checkout)"
echo "    - purchase.html (SaaS landing)"
echo "    - gum.html (redirect variant)"
echo "    - new.html (modern dark theme)"
echo ""

# Step 5: Confirm deployment
echo "${YELLOW}⚠ This will deploy to Cloudflare Pages (signkit-landing)${NC}"
echo ""
read -p "Proceed with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi
echo ""

# Step 6: Deploy
echo "${BLUE}Step 6: Deploying to Cloudflare Pages...${NC}"
echo ""
wrangler pages deploy . --project-name signkit-landing --branch main

# Step 7: Show deployment info
echo ""
echo "${GREEN}✓ Deployment complete!${NC}"
echo ""
echo "View deployments:"
echo "  wrangler pages deployment list --project-name signkit-landing"
echo ""
echo "Check live site:"
echo "  https://signkit.work"
echo ""

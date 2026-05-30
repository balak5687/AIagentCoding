#!/bin/bash
# Quick start script for Multi-Agent SDLC System

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Multi-Agent SDLC System${NC}"
echo "======================================"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    source venv/bin/activate
fi

# Check if config exists
if [ ! -f "config.yaml" ]; then
    echo -e "${YELLOW}config.yaml not found. Copying example...${NC}"
    cp config/config.yaml.example config.yaml
    echo -e "${GREEN}✓ Created config.yaml${NC}"
    echo -e "${YELLOW}⚠ Please edit config.yaml before running${NC}"
    exit 0
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ ! -f ".env.example" ]; then
        echo -e "${YELLOW}.env.example not found. Creating...${NC}"
        cat > .env.example << 'EOF'
# Anthropic API Key (if using API mode)
ANTHROPIC_API_KEY=your_api_key_here

# GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here
EOF
    fi
    echo -e "${YELLOW}.env not found. Copying example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and set your tokens${NC}"
fi

# Load .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No issue provided${NC}"
    echo ""
    echo "Usage:"
    echo "  ./run.sh \"Issue description or URL\""
    echo "  ./run.sh \"https://github.com/owner/repo/issues/123\""
    echo "  ./run.sh \"Add user authentication\" --debug"
    echo ""
    exit 1
fi

# Run the system
echo -e "${GREEN}Starting SDLC system...${NC}"
echo ""
python -m src.main --issue "$@"

#!/bin/bash

# BioFetch Quick Start Script
# Save this as: quick-start.sh in your project root
# Make executable: chmod +x quick-start.sh
# Run with: ./quick-start.sh

set -e

echo "🧬 BioFetch Quick Start"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Docker is installed
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    print_success "Docker and Docker Compose found"
    USE_DOCKER=true
else
    print_warning "Docker not found. Will provide manual setup instructions."
    USE_DOCKER=false
fi

# Create directory structure
print_info "Creating directory structure..."
mkdir -p backend/downloads
mkdir -p frontend/src/components/ui
mkdir -p frontend/src/lib
mkdir -p frontend/public
mkdir -p data/db

print_success "Directories created"

# Create backend .env if not exists
if [ ! -f "backend/.env" ]; then
    print_info "Creating backend/.env..."
    cat > backend/.env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=biofetch
CORS_ORIGINS=*
APP_NAME=BioFetch
APP_VERSION=1.0.0
DEBUG=True
EOF
    print_success "backend/.env created"
fi

# Create frontend .env if not exists
if [ ! -f "frontend/.env" ]; then
    print_info "Creating frontend/.env..."
    cat > frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=0
CHOKIDAR_USEPOLLING=true
EOF
    print_success "frontend/.env created"
fi

# Create .gitkeep for downloads
touch backend/downloads/.gitkeep

print_success "Configuration files ready"

if [ "$USE_DOCKER" = true ]; then
    echo ""
    print_info "Starting with Docker..."
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found!"
        echo "Please copy docker-compose.yml from the artifacts to this directory."
        exit 1
    fi
    
    # Check if containers are already running
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        print_warning "Containers already running. Stopping them first..."
        docker-compose down
    fi
    
    # Build and start
    print_info "Building and starting containers (this may take a few minutes)..."
    docker-compose up -d --build
    
    # Wait for services
    print_info "Waiting for services to start..."
    echo "This may take 30-60 seconds..."
    sleep 15
    
    # Check health with retries
    print_info "Checking service health..."
    
    # Check backend (with retries)
    RETRIES=10
    BACKEND_UP=false
    for i in $(seq 1 $RETRIES); do
        if curl -s http://localhost:8001/api/ > /dev/null 2>&1; then
            print_success "Backend is running!"
            BACKEND_UP=true
            break
        else
            echo "Waiting for backend... ($i/$RETRIES)"
            sleep 3
        fi
    done
    
    if [ "$BACKEND_UP" = false ]; then
        print_error "Backend is not responding after $RETRIES attempts"
        echo "Check logs with: docker-compose logs backend"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is running!"
    else
        print_warning "Frontend might still be compiling (this can take 1-2 minutes)..."
        echo "Check logs with: docker-compose logs frontend"
    fi
    
    echo ""
    echo "================================"
    print_success "BioFetch Docker containers are up!"
    echo "================================"
    echo ""
    echo "🌐 Web Interface:  http://localhost:3000"
    echo "📚 API Docs:       http://localhost:8001/docs"
    echo "🔌 API Endpoint:   http://localhost:8001/api"
    echo ""
    echo "📋 Useful Docker commands:"
    echo "  docker-compose logs -f              # View all logs"
    echo "  docker-compose logs -f backend      # View backend logs"
    echo "  docker-compose logs -f frontend     # View frontend logs"
    echo "  docker-compose down                 # Stop all services"
    echo "  docker-compose restart              # Restart services"
    echo "  docker-compose ps                   # Check status"
    echo ""
    echo "⚠️  If frontend shows 'Compiling...', wait 1-2 minutes and refresh"
    echo ""
    
else
    echo ""
    print_info "Docker not available. Manual setup instructions:"
    echo ""
    echo "================================"
    echo "MANUAL SETUP STEPS"
    echo "================================"
    echo ""
    echo "You'll need 3 separate terminal windows:"
    echo ""
    echo "📍 TERMINAL 1 - MongoDB:"
    echo "  cd $(pwd)"
    echo "  mongod --dbpath ./data/db"
    echo ""
    echo "📍 TERMINAL 2 - Backend:"
    echo "  cd $(pwd)/backend"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "  pip install -r requirements.txt"
    echo "  uvicorn server:app --reload --port 8001"
    echo ""
    echo "📍 TERMINAL 3 - Frontend:"
    echo "  cd $(pwd)/frontend"
    echo "  npm install  # or: yarn install"
    echo "  npm start    # or: yarn start"
    echo ""
    echo "After all 3 are running:"
    echo "  🌐 Web Interface:  http://localhost:3000"
    echo "  📚 API Docs:       http://localhost:8001/docs"
    echo ""
fi

# Test CLI if it exists
if [ -f "biofetch_cli.py" ]; then
    echo ""
    print_info "Testing CLI tool..."
    
    if [ "$USE_DOCKER" = true ]; then
        sleep 5  # Give backend more time
    fi
    
    if python3 biofetch_cli.py test 2>/dev/null; then
        print_success "CLI is working!"
        echo ""
        echo "📋 Try these CLI commands:"
        echo "  python3 biofetch_cli.py databases"
        echo "  python3 biofetch_cli.py download --accession SRR000001 --db sra"
        echo "  python3 biofetch_cli.py jobs"
        echo "  python3 biofetch_cli.py stats"
    else
        print_warning "CLI test failed (services might still be starting)"
        echo "Wait 30 seconds and try: python3 biofetch_cli.py test"
    fi
else
    print_warning "biofetch_cli.py not found. Copy it from artifacts to use CLI."
fi

echo ""
echo "================================"
print_success "Setup Complete! 🎉"
echo "================================"
echo ""

if [ "$USE_DOCKER" = true ]; then
    print_info "Quick verification:"
    echo "  curl http://localhost:8001/api/"
    echo ""
    print_info "If services aren't ready yet, wait a minute and try again."
fi

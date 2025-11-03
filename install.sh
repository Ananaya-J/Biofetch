#!/bin/bash
# BioFetch Installation Script
# This script sets up the complete BioFetch application

set -e  # Exit on error

echo "🧬 BioFetch Installation Script"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
print_info "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { print_error "Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { print_error "Node.js is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { print_error "npm is required but not installed."; exit 1; }

print_success "Prerequisites check passed"

# Setup backend
print_info "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
fi

source venv/bin/activate
pip install -r requirements.txt
print_success "Backend dependencies installed"

# Create .env if not exists
if [ ! -f ".env" ]; then
    cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=biofetch
CORS_ORIGINS=*
EOF
    print_success "Backend .env file created"
fi

cd ..

# Setup frontend
print_info "Setting up frontend..."
cd frontend

npm install
print_success "Frontend dependencies installed"

# Create .env if not exists
if [ ! -f ".env" ]; then
    cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
EOF
    print_success "Frontend .env file created"
fi

cd ..

# Create downloads directory
mkdir -p backend/downloads
print_success "Downloads directory created"

# Create start scripts
print_info "Creating start scripts..."

# Start all script
cat > start_all.sh << 'EOF'
#!/bin/bash
# Start all BioFetch services

# Start MongoDB (if not running)
if ! pgrep -x "mongod" > /dev/null; then
    echo "Starting MongoDB..."
    mongod --fork --logpath /tmp/mongodb.log --dbpath ./data/db
fi

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn server:app --reload --port 8001 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 BioFetch is starting!"
echo "================================"
echo "Backend:  http://localhost:8001"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait

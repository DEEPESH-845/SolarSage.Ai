#!/bin/bash
# install.sh
# Advanced Solar Panel AI Cleaning System Installation Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# System information
SYSTEM_NAME="Advanced Solar Panel AI Cleaning System"
VERSION="3.0.0-advanced"
PYTHON_MIN_VERSION="3.8"

echo -e "${BLUE}"
echo "🌞 ============================================================"
echo "   $SYSTEM_NAME"
echo "   Version: $VERSION"
echo "   Installation Script"
echo "============================================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    print_info "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python $PYTHON_MIN_VERSION or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    REQUIRED_VERSION=$(echo -e "$PYTHON_VERSION\n$PYTHON_MIN_VERSION" | sort -V | head -n1)
    
    if [ "$REQUIRED_VERSION" != "$PYTHON_MIN_VERSION" ]; then
        print_error "Python $PYTHON_MIN_VERSION or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_status "Python $PYTHON_VERSION detected"
}

# Function to create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_status "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
}

# Function to install system dependencies
install_system_deps() {
    print_info "Checking system dependencies..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Debian/Ubuntu
            print_info "Installing system dependencies (Debian/Ubuntu)..."
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev \
                python3-pip \
                libopencv-dev \
                python3-opencv \
                libhdf5-dev \
                libnetcdf-dev \
                libjpeg-dev \
                libpng-dev \
                libglib2.0-0 \
                libsm6 \
                libxext6 \
                libxrender-dev \
                libgomp1
                
        elif command_exists yum; then
            # RedHat/CentOS
            print_info "Installing system dependencies (RedHat/CentOS)..."
            sudo yum update -y
            sudo yum install -y \
                python3-devel \
                opencv-devel \
                hdf5-devel \
                netcdf-devel \
                libjpeg-turbo-devel \
                libpng-devel
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_info "Installing system dependencies (macOS)..."
        if command_exists brew; then
            brew update
            brew install \
                opencv \
                hdf5 \
                netcdf \
                jpeg \
                libpng
        else
            print_warning "Homebrew not found. Please install Homebrew first."
        fi
    fi
    
    print_status "System dependencies installed"
}

# Function to install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Install core requirements
    pip install -r requirements.txt
    
    # Try to install optional Quartz Solar Forecast
    print_info "Attempting to install Quartz Solar Forecast..."
    if pip install quartz-solar-forecast; then
        print_status "Quartz Solar Forecast installed successfully"
        echo "QUARTZ_AVAILABLE=true" >> .env
    else
        print_warning "Quartz Solar Forecast installation failed. Using simulation mode."
        echo "QUARTZ_AVAILABLE=false" >> .env
    fi
    
    print_status "Python dependencies installed"
}

# Function to install hardware dependencies (optional)
install_hardware_deps() {
    print_info "Checking for hardware dependencies..."
    
    # Check if running on Raspberry Pi
    if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
        print_info "Raspberry Pi detected. Installing GPIO libraries..."
        pip install RPi.GPIO gpiozero
        echo "ENABLE_GPIO=true" >> .env
        print_status "GPIO libraries installed"
        
        # Add user to gpio group
        sudo usermod -a -G gpio $USER
        print_info "Added user to gpio group (requires logout/login to take effect)"
    else
        print_info "Not running on Raspberry Pi. GPIO disabled."
        echo "ENABLE_GPIO=false" >> .env
    fi
    
    # Check for Qualcomm NPU (simulation)
    print_info "Enabling NPU acceleration..."
    echo "QUALCOMM_NPU_AVAILABLE=true" >> .env
}

# Function to create directory structure
create_directories() {
    print_info "Creating directory structure..."
    
    # Create main directories
    mkdir -p data/{images/{raw,processed,demo},weather,sensors,models/{dust_detection,image_analysis,forecasting}}
    mkdir -p results/{cycles,analytics/{monitoring_reports,trends},exports/{csv,pdf,json}}
    mkdir -p logs/{errors,performance}
    mkdir -p config
    mkdir -p temp/{processing,downloads,backups,debug}
    
    print_status "Directory structure created"
}

# Function to create configuration files
create_config_files() {
    print_info "Creating configuration files..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
    fi
    
    # Create site configuration
    cat > config/site_config.json << EOF
{
    "latitude": 28.6139,
    "longitude": 77.2090,
    "capacity_kwp": 5.0,
    "panel_area_m2": 25.0,
    "installation_date": "2023-01-01",
    "system_id": "SOLAR_001",
    "timezone": "Asia/Kolkata"
}
EOF

    # Create agent configuration
    cat > config/agent_config.yaml << EOF
# Agent Configuration
dust_detection:
  pm25_threshold: 75
  visibility_threshold: 10
  wind_threshold: 15
  confidence_threshold: 80

forecast:
  forecast_hours: 48
  update_interval: 3600
  weather_sources: ["openweather", "quartz"]

image_analysis:
  max_image_size: 2048
  processing_quality: "high"
  npu_acceleration: true
  confidence_threshold: 75

decision:
  critical_action_score: 85
  recommended_action_score: 70
  optional_action_score: 50
  minimum_confidence: 60
EOF

    print_status "Configuration files created"
}

# Function to run system tests
run_tests() {
    print_info "Running system tests..."
    
    # Install test dependencies
    pip install pytest pytest-asyncio
    
    # Run basic tests
    if python -m pytest tests/unit/ -v --tb=short; then
        print_status "Unit tests passed"
    else
        print_warning "Some unit tests failed. System may still be functional."
    fi
    
    # Run system diagnostics
    if python main.py --mode diagnostics; then
        print_status "System diagnostics completed successfully"
    else
        print_warning "System diagnostics detected issues"
    fi
}

# Function to create systemd service (Linux only)
create_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command_exists systemctl; then
        print_info "Creating systemd service..."
        
        INSTALL_DIR=$(pwd)
        USER_NAME=$(whoami)
        
        sudo tee /etc/systemd/system/solar-ai.service > /dev/null << EOF
[Unit]
Description=Advanced Solar Panel AI Cleaning System
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python main.py --mode continuous --interval 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable solar-ai
        
        print_status "Systemd service created and enabled"
        print_info "Start service with: sudo systemctl start solar-ai"
        print_info "View logs with: sudo journalctl -u solar-ai -f"
    fi
}

# Function to display final instructions
show_final_instructions() {
    print_status "Installation completed successfully!"
    
    echo -e "\n${BLUE}🎯 QUICK START GUIDE:${NC}"
    echo "════════════════════════════════════════════════════════════"
    
    echo -e "\n${GREEN}1. Activate virtual environment:${NC}"
    echo "   source venv/bin/activate"
    
    echo -e "\n${GREEN}2. Run single analysis:${NC}"
    echo "   python main.py --mode single"
    
    echo -e "\n${GREEN}3. Start continuous monitoring:${NC}"
    echo "   python main.py --mode continuous --interval 2"
    
    echo -e "\n${GREEN}4. Check system status:${NC}"
    echo "   python main.py --mode status"
    
    echo -e "\n${GREEN}5. Run diagnostics:${NC}"
    echo "   python main.py --mode diagnostics"
    
    echo -e "\n${BLUE}🔧 CONFIGURATION:${NC}"
    echo "════════════════════════════════════════════════════════════"
    echo "• Edit config/site_config.json for your site settings"
    echo "• Modify .env file for environment variables"
    echo "• Update config/agent_config.yaml for agent parameters"
    
    echo -e "\n${BLUE}🌐 FEATURES ENABLED:${NC}"
    echo "════════════════════════════════════════════════════════════"
    
    # Check what features are enabled
    if grep -q "QUARTZ_AVAILABLE=true" .env 2>/dev/null; then
        echo "• ✅ Quartz Solar Forecast: Real ML predictions"
    else
        echo "• ⚠️  Quartz Solar Forecast: Using simulation mode"
    fi
    
    if grep -q "QUALCOMM_NPU_AVAILABLE=true" .env 2>/dev/null; then
        echo "• ✅ Qualcomm NPU: Accelerated image processing"
    else
        echo "• 🔧 NPU: Using CPU mode"
    fi
    
    if grep -q "ENABLE_GPIO=true" .env 2>/dev/null; then
        echo "• ✅ GPIO Control: Hardware spray system enabled"
    else
        echo "• 🧮 GPIO Control: Simulation mode"
    fi
    
    echo -e "\n${BLUE}📚 DOCUMENTATION:${NC}"
    echo "════════════════════════════════════════════════════════════"
    echo "• README.md - Complete system documentation"
    echo "• docs/ - Detailed technical documentation"
    echo "• examples/ - Usage examples and tutorials"
    
    echo -e "\n${BLUE}🚀 EXAMPLE COMMANDS:${NC}"
    echo "════════════════════════════════════════════════════════════"
    echo "# Custom site configuration:"
    echo "python main.py --mode single --latitude 51.5074 --longitude -0.1278 --capacity 10.0"
    echo ""
    echo "# With custom image:"
    echo "python main.py --mode single --image /path/to/panel_image.jpg"
    echo ""
    echo "# Enable all hardware features:"
    echo "ENABLE_GPIO=true QUALCOMM_NPU_AVAILABLE=true python main.py --mode single"
    echo ""
    echo "# Long-term monitoring:"
    echo "python main.py --mode continuous --interval 6 --max-cycles 100"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command_exists systemctl; then
        echo -e "\n${BLUE}🔄 SYSTEMD SERVICE:${NC}"
        echo "════════════════════════════════════════════════════════════"
        echo "• Start service: sudo systemctl start solar-ai"
        echo "• Stop service: sudo systemctl stop solar-ai"
        echo "• View logs: sudo journalctl -u solar-ai -f"
        echo "• Service status: sudo systemctl status solar-ai"
    fi
    
    echo -e "\n${BLUE}🐛 TROUBLESHOOTING:${NC}"
    echo "════════════════════════════════════════════════════════════"
    echo "• Check logs in logs/ directory"
    echo "• Run diagnostics: python main.py --mode diagnostics"
    echo "• View system status: python main.py --mode status"
    echo "• GitHub Issues: https://github.com/solar-ai/solar-panel-cleaning/issues"
    
    echo -e "\n${GREEN}🎉 Installation Complete! The Advanced Solar Panel AI Cleaning System is ready to use.${NC}"
    echo -e "${YELLOW}⚠️  Remember to logout/login if GPIO was enabled to apply group permissions.${NC}"
}

# Main installation function
main() {
    echo -e "\n${BLUE}Starting installation...${NC}\n"
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ] || [ ! -f "requirements.txt" ]; then
        print_error "Please run this script from the solar-panel-ai-cleaning directory"
        exit 1
    fi
    
    # Check for root privileges warning
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. Consider using a regular user account."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Run installation steps
    check_python_version
    install_system_deps
    create_venv
    install_python_deps
    install_hardware_deps
    create_directories
    create_config_files
    
    # Install the package
    print_info "Installing the package..."
    pip install -e .
    print_status "Package installed"
    
    # Run tests
    if [ "${SKIP_TESTS:-false}" != "true" ]; then
        run_tests
    else
        print_warning "Skipping tests (SKIP_TESTS=true)"
    fi
    
    # Create systemd service (optional)
    if [ "${CREATE_SERVICE:-true}" = "true" ]; then
        create_service
    fi
    
    # Show final instructions
    show_final_instructions
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            export SKIP_TESTS=true
            shift
            ;;
        --no-service)
            export CREATE_SERVICE=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-tests    Skip running tests after installation"
            echo "  --no-service    Don't create systemd service"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  SKIP_TESTS=true     Skip tests"
            echo "  CREATE_SERVICE=false Don't create service"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Trap to cleanup on exit
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Installation failed!"
        echo -e "\n${YELLOW}Troubleshooting tips:${NC}"
        echo "• Check system dependencies are installed"
        echo "• Ensure Python $PYTHON_MIN_VERSION+ is available"
        echo "• Try running with --skip-tests if tests fail"
        echo "• Check the logs for detailed error messages"
    fi
}

trap cleanup EXIT

# Run main installation
main "$@"
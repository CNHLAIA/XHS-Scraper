# XHS Scraper - Deployment & Installation Guide

**Version**: 1.0  
**Last Updated**: February 6, 2025  
**Status**: ✅ Production Ready

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)
8. [Maintenance](#maintenance)
9. [Support](#support)

---

## 🚀 Quick Start

### 30-Second Setup
```bash
# 1. Clone or download the project
git clone https://github.com/yourusername/xhs-scraper.git
cd xhs-scraper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Extract XHS cookies
# Follow COOKIE_EXTRACTION_GUIDE.md

# 4. Configure and run
python scripts/get_user_info.py
```

### For Experienced Users
```bash
pip install -e .
export XHS_COOKIE="your_cookie_here"
python scripts/get_notes.py
```

---

## 📋 System Requirements

### Required
- **Python**: 3.8 or higher
- **pip**: Latest version
- **OS**: Windows, macOS, or Linux
- **RAM**: 512 MB minimum
- **Disk Space**: 100 MB for installation
- **Internet**: Active connection required

### Recommended
- **Python**: 3.10 or higher
- **RAM**: 2 GB or higher
- **Disk Space**: 500 MB for logs and caches
- **Network**: Stable, high-speed connection

### Optional
- **Git**: For cloning repository
- **Docker**: For containerized deployment
- **Virtual Environment**: For isolated setup

### Verify Installation
```bash
python --version          # Should show 3.8+
pip --version             # Should show latest
python -c "import sys; print(sys.platform)"  # Your OS
```

---

## 📦 Installation Methods

### Method 1: Standard Installation (Recommended)

#### Step 1: Clone Repository
```bash
# Using Git
git clone https://github.com/yourusername/xhs-scraper.git
cd xhs-scraper

# OR download ZIP and extract
# Then navigate to the directory
cd xhs-scraper
```

#### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Verify Installation
```bash
python -c "from xhs_scraper import XhsClient; print('✅ Installation successful')"
```

### Method 2: Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/yourusername/xhs-scraper.git
cd xhs-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify
python -m pytest tests/ -v
```

### Method 3: Docker Installation

For containerized deployment:

```bash
# Build image
docker build -t xhs-scraper .

# Run container
docker run -it \
  -e XHS_COOKIE="your_cookie_here" \
  -v $(pwd)/output:/app/output \
  xhs-scraper python scripts/get_notes.py
```

### Method 4: Pip Installation (From PyPI)

When published to PyPI:

```bash
pip install xhs-scraper

# Then import in your code
from xhs_scraper import XhsClient
```

---

## ⚙️ Configuration

### Step 1: Extract XHS Cookies

**Detailed instructions**: See [COOKIE_EXTRACTION_GUIDE.md](./COOKIE_EXTRACTION_GUIDE.md)

Quick steps:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to xiaohongshu.com
4. Look for API request headers
5. Copy the `cookie` header value

### Step 2: Configure Environment

#### Option A: Environment Variables
```bash
# Windows (Command Prompt)
set XHS_COOKIE="your_cookie_here"

# Windows (PowerShell)
$env:XHS_COOKIE="your_cookie_here"

# macOS/Linux
export XHS_COOKIE="your_cookie_here"
```

#### Option B: Configuration File
Create `config.json`:
```json
{
  "cookie": "your_cookie_here",
  "timeout": 30,
  "proxy": null,
  "retry_count": 3
}
```

Use in code:
```python
import json
from xhs_scraper import XhsClient

with open('config.json') as f:
    config = json.load(f)

client = XhsClient(cookie=config['cookie'])
```

#### Option C: Code Configuration
```python
from xhs_scraper import XhsClient

client = XhsClient(cookie="your_cookie_here")
```

### Step 3: Optional Configuration

#### Proxy Setup
```python
from xhs_scraper import XhsClient

client = XhsClient(
    cookie="your_cookie_here",
    proxy="http://proxy.example.com:8080"
)
```

#### Custom Headers
```python
client = XhsClient(
    cookie="your_cookie_here",
    headers={
        "User-Agent": "Custom User Agent"
    }
)
```

#### Rate Limiting
```python
from xhs_scraper.rate_limiter import RateLimiter

limiter = RateLimiter(requests_per_second=1)
# Automatically applied when using client
```

---

## ✅ Verification

### 1. Test Python Installation
```bash
python --version
# Expected: Python 3.8 or higher
```

### 2. Test Package Installation
```bash
python -c "from xhs_scraper import XhsClient; print('✅ Package imported successfully')"
```

### 3. Test Configuration
```bash
# Create test script
cat > test_config.py << 'EOF'
from xhs_scraper import XhsClient
import os

cookie = os.getenv('XHS_COOKIE')
if not cookie:
    print("❌ XHS_COOKIE not configured")
else:
    try:
        client = XhsClient(cookie=cookie)
        print("✅ Configuration successful")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
EOF

python test_config.py
```

### 4. Run Test Suite (Optional)
```bash
# Run all tests
python -m pytest tests/ -v

# Expected: 195 passed in ~11.33s

# Run specific test category
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

### 5. Test Basic Functionality
```bash
# Create test script
cat > test_functionality.py << 'EOF'
import os
from xhs_scraper import XhsClient

cookie = os.getenv('XHS_COOKIE')
if not cookie:
    print("❌ XHS_COOKIE not set")
else:
    try:
        client = XhsClient(cookie=cookie)
        # Test with a known user
        result = client.get_user_info("xiaohongshu")
        print(f"✅ API working - Got user: {result}")
    except Exception as e:
        print(f"⚠️ API Error (may be network): {e}")
EOF

python test_functionality.py
```

### 6. Verify All Components
```bash
# Script to verify all components
cat > verify_installation.py << 'EOF'
import sys
import importlib
from pathlib import Path

checks = {
    "Python Version": lambda: sys.version_info >= (3, 8),
    "xhs_scraper package": lambda: importlib.import_module('xhs_scraper'),
    "pytest": lambda: importlib.import_module('pytest'),
    "requests": lambda: importlib.import_module('requests'),
}

print("🔍 Verification Report")
print("=" * 40)

passed = 0
for name, check in checks.items():
    try:
        check()
        print(f"✅ {name}")
        passed += 1
    except Exception as e:
        print(f"❌ {name}: {e}")

print("=" * 40)
print(f"Result: {passed}/{len(checks)} checks passed")

if passed == len(checks):
    print("🎉 Installation verified successfully!")
else:
    print("⚠️ Some components need attention")
EOF

python verify_installation.py
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Python Version Too Old
```
Error: Python 3.8 or higher required
```

**Solution**:
```bash
# Check current version
python --version

# Install Python 3.10+
# Windows: https://www.python.org/downloads/
# macOS: brew install python@3.10
# Linux: apt-get install python3.10
```

#### Issue 2: Module Not Found
```
Error: ModuleNotFoundError: No module named 'xhs_scraper'
```

**Solution**:
```bash
# Reinstall package
pip uninstall xhs_scraper
pip install -e .

# Or verify installation
python -c "import xhs_scraper; print(xhs_scraper.__file__)"
```

#### Issue 3: Permission Denied
```
Error: Permission denied when installing
```

**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue 4: Cookie Configuration Error
```
Error: XHS_COOKIE not found or invalid
```

**Solution**:
```bash
# Verify cookie is set
echo $XHS_COOKIE  # macOS/Linux
echo %XHS_COOKIE%  # Windows

# Extract fresh cookies (see COOKIE_EXTRACTION_GUIDE.md)
# Update environment variable
export XHS_COOKIE="new_cookie_value"

# Test configuration
python test_config.py
```

#### Issue 5: Network Connectivity Error
```
Error: Connection refused or timeout
```

**Solution**:
```bash
# Verify internet connection
ping google.com

# Check proxy settings
# Try with timeout parameter
from xhs_scraper import XhsClient
client = XhsClient(cookie="...", timeout=60)

# Try with proxy if needed
client = XhsClient(
    cookie="...",
    proxy="http://proxy.example.com:8080"
)
```

#### Issue 6: API Rate Limit
```
Error: Rate limit exceeded or too many requests
```

**Solution**:
```bash
# The client includes automatic rate limiting
# Default: 1 request per second
# This is configurable via RateLimiter

# For testing, you can adjust:
from xhs_scraper.rate_limiter import RateLimiter
limiter = RateLimiter(requests_per_second=0.5)  # Slower requests
```

#### Issue 7: SSL/Certificate Error
```
Error: SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution**:
```bash
# Update certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Or disable SSL verification (not recommended for production)
import urllib3
urllib3.disable_warnings()

# Better: Update certifi
pip install --upgrade certifi
```

### Verification Commands

```bash
# Check Python version
python --version

# Check package installation
pip list | grep xhs-scraper

# Check cookie configuration
echo $XHS_COOKIE

# Check network connectivity
ping xiaohongshu.com

# Run diagnostics
python verify_installation.py
```

---

## 🚢 Production Deployment

### Pre-Deployment Checklist

- [ ] Python 3.8+ installed and verified
- [ ] Virtual environment configured
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] XHS cookies extracted and validated
- [ ] Environment variables configured
- [ ] Configuration files created
- [ ] Logging configured
- [ ] Monitoring setup complete
- [ ] Backup and rollback procedures documented

### Deployment Steps

#### Step 1: Prepare Environment
```bash
# Create production directory
mkdir -p /opt/xhs-scraper
cd /opt/xhs-scraper

# Clone repository
git clone --depth 1 https://github.com/yourusername/xhs-scraper.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Step 2: Configure Application
```bash
# Copy configuration template
cp config.example.json config.json

# Edit configuration
nano config.json

# Set environment variables
export XHS_COOKIE="your_production_cookie"
export LOG_LEVEL="INFO"
export LOG_FILE="/var/log/xhs-scraper/app.log"
```

#### Step 3: Run Tests
```bash
# Run full test suite
python -m pytest tests/ -v

# Expected: 195 passed in ~11.33s

# If all pass, proceed to deployment
```

#### Step 4: Start Application
```bash
# Option A: Direct execution
python scripts/get_notes.py

# Option B: With logging
python -u scripts/get_notes.py 2>&1 | tee -a logs/app.log

# Option C: Daemonize with systemd
# Create /etc/systemd/system/xhs-scraper.service
# Then: sudo systemctl start xhs-scraper
```

#### Step 5: Monitor Deployment
```bash
# Check application status
ps aux | grep xhs-scraper

# Check logs
tail -f logs/app.log

# Verify output
ls -la output/
```

### Systemd Service Setup (Linux)

Create `/etc/systemd/system/xhs-scraper.service`:
```ini
[Unit]
Description=XHS Scraper Service
After=network.target

[Service]
Type=simple
User=xhs-scraper
WorkingDirectory=/opt/xhs-scraper
Environment="PATH=/opt/xhs-scraper/venv/bin"
Environment="XHS_COOKIE=your_cookie_here"
ExecStart=/opt/xhs-scraper/venv/bin/python scripts/get_notes.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable xhs-scraper
sudo systemctl start xhs-scraper
sudo systemctl status xhs-scraper
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV XHS_COOKIE=""

CMD ["python", "scripts/get_notes.py"]
```

Deploy:
```bash
# Build image
docker build -t xhs-scraper:latest .

# Run container
docker run -d \
  --name xhs-scraper \
  -e XHS_COOKIE="your_cookie" \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  xhs-scraper:latest

# Check status
docker ps
docker logs xhs-scraper

# Stop container
docker stop xhs-scraper
docker rm xhs-scraper
```

---

## 🔄 Maintenance

### Regular Maintenance Tasks

#### Weekly
- [ ] Check logs for errors
- [ ] Verify application is running
- [ ] Test with manual script execution
- [ ] Monitor disk space and storage

#### Monthly
- [ ] Review and update cookies (they expire)
- [ ] Check for new XHS API changes
- [ ] Review error logs
- [ ] Backup important data

#### Quarterly
- [ ] Update dependencies (`pip install --upgrade -r requirements.txt`)
- [ ] Run full test suite
- [ ] Review and update documentation
- [ ] Performance analysis and optimization

### Cookie Refresh

XHS cookies expire and need periodic refresh:

```bash
# Extract new cookies
# Follow COOKIE_EXTRACTION_GUIDE.md

# Update environment variable
export XHS_COOKIE="new_cookie_value"

# Or update config file
nano config.json
# Update cookie field

# Restart application
systemctl restart xhs-scraper
# Or manually restart the script
```

### Log Rotation

Create `/etc/logrotate.d/xhs-scraper`:
```
/var/log/xhs-scraper/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 xhs-scraper xhs-scraper
    sharedscripts
    postrotate
        systemctl reload xhs-scraper > /dev/null 2>&1 || true
    endscript
}
```

### Backup Strategy

```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz /opt/xhs-scraper

# Store backups
cp backup-$(date +%Y%m%d).tar.gz /backup/xhs-scraper/

# List backups
ls -lah /backup/xhs-scraper/

# Restore from backup
tar -xzf backup-20250206.tar.gz -C /
```

---

## 🚨 Rollback Procedures

### Quick Rollback

```bash
# Stop application
systemctl stop xhs-scraper

# Restore from backup
tar -xzf backup-20250206.tar.gz -C /

# Restart application
systemctl start xhs-scraper

# Verify status
systemctl status xhs-scraper
```

### Version Rollback

```bash
# Check git history
git log --oneline

# Rollback to previous version
git checkout <commit_hash>

# Reinstall dependencies
pip install -r requirements.txt

# Restart application
systemctl restart xhs-scraper
```

---

## 📞 Support Resources

### Documentation
- 📖 [COOKIE_EXTRACTION_GUIDE.md](./COOKIE_EXTRACTION_GUIDE.md) - How to extract cookies
- 📖 [ERROR_REFERENCE.md](./ERROR_REFERENCE.md) - Error troubleshooting
- 📖 [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) - Full documentation
- 📖 [TEST_RESULTS_REPORT.md](./TEST_RESULTS_REPORT.md) - Test documentation

### Getting Help
1. **Check Documentation** - Most answers in the guides above
2. **Review Error Reference** - Detailed error troubleshooting
3. **Check Logs** - Application logs for detailed error info
4. **Run Tests** - Verify installation with test suite
5. **GitHub Issues** - Report bugs or ask questions

### Common Commands

```bash
# View help
python scripts/get_notes.py --help

# Check logs
tail -f logs/app.log

# Run diagnostics
python verify_installation.py

# Run tests
python -m pytest tests/ -v

# Clean up old files
rm -f logs/*.log.old
rm -rf output/*.json.bak
```

---

## ✅ Deployment Verification Checklist

After deployment, verify:

- [ ] Application starts without errors
- [ ] Tests pass (195/195)
- [ ] Configuration is correct
- [ ] Logs show normal operation
- [ ] API calls are successful
- [ ] Output files are created
- [ ] No unhandled exceptions
- [ ] Performance is acceptable
- [ ] Monitoring is active
- [ ] Backup is available

---

## 📝 Additional Notes

### Security Best Practices
- Never commit cookies to version control
- Use environment variables for secrets
- Use HTTPS only for production
- Implement rate limiting
- Monitor for suspicious activity
- Regular security updates

### Performance Optimization
- Use rate limiting to prevent blocks
- Implement caching where appropriate
- Use connection pooling
- Monitor memory usage
- Profile code for bottlenecks

### Scaling Considerations
- Use process queues for multiple requests
- Implement worker pool pattern
- Use load balancing for multiple instances
- Monitor API rate limits
- Implement circuit breaker pattern

---

## 🎯 Next Steps

1. **Follow Installation Method 1** for standard setup
2. **Extract XHS Cookies** using COOKIE_EXTRACTION_GUIDE.md
3. **Configure Environment** with your cookies
4. **Run Verification** to ensure everything works
5. **Read Documentation** to understand capabilities
6. **Start Using Scripts** in the `scripts/` directory

---

**For detailed support, see [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)**

**Questions?** Check [ERROR_REFERENCE.md](./ERROR_REFERENCE.md) for troubleshooting

**Version**: 1.0 | **Last Updated**: February 6, 2025 | **Status**: ✅ Production Ready


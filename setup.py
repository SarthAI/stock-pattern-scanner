"""
Setup Script for Stock Pattern Scanner
Helps with initial configuration
"""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """Create necessary directories"""
    print("Creating directory structure...")

    directories = [
        '.streamlit',
        'logs'
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✓ Created: {directory}/")

    print()


def create_secrets_file():
    """Create secrets.toml template"""
    print("Setting up secrets.toml...")

    secrets_path = Path('.streamlit/secrets.toml')

    if secrets_path.exists():
        print(f"  ⚠ {secrets_path} already exists. Skipping.")
        print()
        return

    template = """# Streamlit Secrets Configuration
# Fill in your actual credentials below

# Email Configuration
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-16-char-app-password"
RECIPIENT_EMAIL = "recipient-email@gmail.com"

# SMTP Configuration (default values)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Instructions:
# 1. Replace email addresses with your actual Gmail addresses
# 2. Generate Gmail App Password:
#    - Go to: https://myaccount.google.com/apppasswords
#    - Create app password for "Mail"
#    - Use the 16-character password (remove spaces)
# 3. Save this file
# 4. Run: python test_email.py (to verify configuration)
"""

    with open(secrets_path, 'w') as f:
        f.write(template)

    print(f"  ✓ Created: {secrets_path}")
    print(f"  ⚠ Please edit this file with your actual credentials!")
    print()


def create_config_file():
    """Create config.toml"""
    print("Setting up config.toml...")

    config_path = Path('.streamlit/config.toml')

    if config_path.exists():
        print(f"  ⚠ {config_path} already exists. Skipping.")
        print()
        return

    config = """# Streamlit Configuration

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 5

[browser]
gatherUsageStats = false
"""

    with open(config_path, 'w') as f:
        f.write(config)

    print(f"  ✓ Created: {config_path}")
    print()


def check_dependencies():
    """Check if dependencies are installed"""
    print("Checking dependencies...")

    try:
        import streamlit
        print("  ✓ streamlit")
    except ImportError:
        print("  ✗ streamlit - NOT INSTALLED")
        return False

    try:
        import pandas
        print("  ✓ pandas")
    except ImportError:
        print("  ✗ pandas - NOT INSTALLED")
        return False

    try:
        import yfinance
        print("  ✓ yfinance")
    except ImportError:
        print("  ✗ yfinance - NOT INSTALLED")
        return False

    try:
        import scipy
        print("  ✓ scipy")
    except ImportError:
        print("  ✗ scipy - NOT INSTALLED")
        return False

    try:
        import apscheduler
        print("  ✓ apscheduler")
    except ImportError:
        print("  ✗ apscheduler - NOT INSTALLED")
        return False

    print()
    return True


def main():
    """Main setup function"""
    print("=" * 60)
    print("Stock Pattern Scanner - Setup")
    print("=" * 60)
    print()

    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ Error: app.py not found!")
        print("Please run this script from the project root directory.")
        print()
        sys.exit(1)

    # Create directories
    create_directory_structure()

    # Create config files
    create_config_file()
    create_secrets_file()

    # Check dependencies
    deps_ok = check_dependencies()

    if not deps_ok:
        print("=" * 60)
        print("⚠ Missing Dependencies!")
        print("=" * 60)
        print()
        print("Install dependencies with:")
        print("  pip install -r requirements.txt")
        print()
        sys.exit(1)

    # Final instructions
    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("1. Configure email credentials:")
    print("   Edit: .streamlit/secrets.toml")
    print()
    print("2. Test email configuration:")
    print("   Run: python test_email.py")
    print()
    print("3. Start the application:")
    print("   Run: streamlit run app.py")
    print()
    print("4. Configure stock list in the app")
    print()
    print("5. Click 'Start' to begin scanning!")
    print()
    print("For deployment instructions, see: DEPLOYMENT.md")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Setup cancelled.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

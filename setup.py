#!/usr/bin/env python3
"""
Setup script for Recipe AI Hub
Automates the installation and configuration process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_virtual_environment():
    """Create virtual environment"""
    if os.path.exists("venv"):
        print("ℹ️  Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    # Determine the correct pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "uploads",
        "instance",
        "static/uploads"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment_file():
    """Create .env file from template"""
    if os.path.exists(".env"):
        print("ℹ️  .env file already exists")
        return True
    
    if os.path.exists("env.example"):
        shutil.copy("env.example", ".env")
        print("✅ Created .env file from template")
        print("⚠️  Please update .env file with your configuration")
        return True
    else:
        print("❌ env.example file not found")
        return False

def generate_secret_key():
    """Generate a secure secret key"""
    import secrets
    return secrets.token_hex(32)

def update_env_file():
    """Update .env file with generated secrets"""
    if not os.path.exists(".env"):
        return False
    
    # Read current .env file
    with open(".env", "r") as f:
        content = f.read()
    
    # Generate new secret keys
    secret_key = generate_secret_key()
    jwt_secret = generate_secret_key()
    
    # Replace placeholder values
    content = content.replace("your-super-secret-key-change-this-in-production", secret_key)
    content = content.replace("your-jwt-secret-key-change-this-in-production", jwt_secret)
    
    # Write updated content
    with open(".env", "w") as f:
        f.write(content)
    
    print("✅ Updated .env file with secure secret keys")
    return True

def initialize_database():
    """Initialize the database"""
    return run_command("python app.py", "Initializing database")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("\n2. Update .env file with your configuration:")
    print("   - Add your Gemini API key (optional)")
    print("   - Configure any additional settings as needed")
    
    print("\n3. Run the application:")
    print("   python app.py")
    
    print("\n4. Open your browser and go to:")
    print("   http://localhost:5000")
    
    print("\n5. Default admin credentials:")
    print("   Email: admin@airecipehub.com")
    print("   Password: admin123")
    
    print("\n📚 For more information, see README.md")
    print("🐛 For troubleshooting, check the README.md troubleshooting section")

def main():
    """Main setup function"""
    print("🚀 Recipe AI Hub Setup")
    print("="*30)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup environment file
    if not setup_environment_file():
        sys.exit(1)
    
    # Update environment file with secure keys
    update_env_file()
    
    # Initialize database
    print("🔄 Initializing database (this may take a moment)...")
    if not initialize_database():
        print("⚠️  Database initialization failed, but you can try running the app manually")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

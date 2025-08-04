#!/usr/bin/env python3
"""
Dependency Manager for Tally Supabase Wizard
Automatically installs and manages required dependencies.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DependencyManager:
    """Manages installation of required dependencies."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.is_64bit = sys.maxsize > 2**32
        
        # Define Python download URLs
        self.python_urls = {
            'windows': {
                'x86_64': 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe',
                'x86': 'https://www.python.org/ftp/python/3.11.8/python-3.11.8.exe'
            },
            'darwin': {
                'x86_64': 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-macos11.pkg',
                'arm64': 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-macos11.pkg'
            },
            'linux': {
                'x86_64': 'https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz',
                'x86': 'https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz',
                'arm64': 'https://www.python.org/ftp/python/3.11.8/Python-3.11.8.tgz'
            }
        }
    
    def check_python_installed(self) -> bool:
        """Check if Python is installed and accessible."""
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Check if Python version is 3.11+
                version_str = result.stdout.strip()
                if 'Python 3.' in version_str:
                    version_parts = version_str.split()[1].split('.')
                    if len(version_parts) >= 2:
                        major, minor = int(version_parts[0]), int(version_parts[1])
                        return major == 3 and minor >= 11
            return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_python_url(self) -> str:
        """Get the appropriate Python download URL for the current system."""
        if self.system not in self.python_urls:
            raise ValueError(f"Unsupported operating system: {self.system}")
        
        # Determine architecture
        if self.system == 'windows':
            arch = 'x86_64' if self.is_64bit else 'x86'
        elif self.system == 'darwin':
            arch = 'arm64' if 'arm' in self.architecture else 'x86_64'
        else:  # Linux
            arch = 'arm64' if 'arm' in self.architecture else 'x86_64'
        
        return self.python_urls[self.system][arch]
    
    def download_file(self, url: str, destination: Path) -> bool:
        """Download a file from URL to destination."""
        try:
            print(f"Downloading {url} to {destination}")
            
            # Create destination directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with progress indicator
            def show_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    print(f"\rDownload progress: {percent}%", end='', flush=True)
            
            urllib.request.urlretrieve(url, destination, show_progress)
            print()  # New line after progress
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def install_python_windows(self, install_dir: Path) -> bool:
        """Install Python on Windows."""
        try:
            url = self.get_python_url()
            installer_path = install_dir / "python_installer.exe"
            
            # Download installer
            if not self.download_file(url, installer_path):
                return False
            
            # Run installer silently
            cmd = [
                str(installer_path),
                '/quiet',
                '/InstallAllUsers=1',
                '/PrependPath=1',
                '/Include_test=0'
            ]
            
            print("Installing Python...")
            result = subprocess.run(cmd, timeout=300)
            
            # Clean up installer
            installer_path.unlink(missing_ok=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Python installation failed: {e}")
            return False
    
    def install_python_darwin(self, install_dir: Path) -> bool:
        """Install Python on macOS."""
        try:
            # Try using Homebrew first
            try:
                result = subprocess.run(['brew', 'install', 'python@3.11'], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    print("Python installed via Homebrew")
                    return True
            except FileNotFoundError:
                pass
            
            # Fallback to manual installation
            url = self.get_python_url()
            pkg_path = install_dir / "python_installer.pkg"
            
            # Download installer
            if not self.download_file(url, pkg_path):
                return False
            
            # Install package
            print("Installing Python...")
            cmd = ['sudo', 'installer', '-pkg', str(pkg_path), '-target', '/']
            result = subprocess.run(cmd, timeout=300)
            
            # Clean up installer
            pkg_path.unlink(missing_ok=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Python installation failed: {e}")
            return False
    
    def install_python_linux(self, install_dir: Path) -> bool:
        """Install Python on Linux."""
        try:
            # Try using package manager first
            package_managers = [
                ['apt', 'update', '&&', 'apt', 'install', '-y', 'python3.11', 'python3.11-venv', 'python3.11-distutils'],
                ['yum', 'install', '-y', 'python3.11'],
                ['dnf', 'install', '-y', 'python3.11']
            ]
            
            for cmd in package_managers:
                try:
                    print(f"Trying {cmd[0]}...")
                    result = subprocess.run(['sudo', 'bash', '-c', ' '.join(cmd)], 
                                          capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        print(f"Python installed via {cmd[0]}")
                        return True
                except FileNotFoundError:
                    continue
            
            # Fallback to source compilation
            print("Installing Python from source...")
            url = self.get_python_url()
            source_path = install_dir / "python_source.tgz"
            
            # Download source
            if not self.download_file(url, source_path):
                return False
            
            # Extract and compile
            extract_dir = install_dir / "python_build"
            extract_dir.mkdir(exist_ok=True)
            
            with tarfile.open(source_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
            
            # Find extracted directory
            python_dir = next(extract_dir.iterdir())
            build_dir = python_dir / "build"
            build_dir.mkdir(exist_ok=True)
            
            # Configure and make
            subprocess.run(['./configure', '--prefix=/usr/local'], 
                         cwd=python_dir, check=True)
            subprocess.run(['make', '-j4'], cwd=python_dir, check=True)
            subprocess.run(['sudo', 'make', 'install'], cwd=python_dir, check=True)
            
            # Clean up
            shutil.rmtree(extract_dir)
            source_path.unlink(missing_ok=True)
            
            return True
            
        except Exception as e:
            print(f"Python installation failed: {e}")
            return False
    
    def install_python(self, install_dir: Path = None) -> bool:
        """Install Python for current platform."""
        if install_dir is None:
            install_dir = Path.home() / ".tally-supabase" / "installers"
        
        install_dir.mkdir(parents=True, exist_ok=True)
        
        if self.system == "windows":
            return self.install_python_windows(install_dir)
        elif self.system == "darwin":
            return self.install_python_darwin(install_dir)
        else:  # Linux
            return self.install_python_linux(install_dir)
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies from requirements.txt."""
        try:
            # Find requirements.txt
            requirements_file = Path("requirements.txt")
            if not requirements_file.exists():
                print("requirements.txt not found")
                return False
            
            # Install dependencies
            print("Installing Python dependencies...")
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("Python dependencies installed successfully")
                return True
            else:
                print(f"Failed to install dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Failed to install Python dependencies: {e}")
            return False
    
    def check_tally_prime_connection(self) -> bool:
        """Check if Tally Prime is accessible."""
        try:
            import socket
            
            # Try to connect to Tally Prime on localhost:9000
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 9000))
            sock.close()
            
            return result == 0
            
        except Exception as e:
            print(f"Tally connection check failed: {e}")
            return False
    
    def get_installation_status(self) -> dict:
        """Get status of all dependencies."""
        return {
            'python_installed': self.check_python_installed(),
            'python_dependencies_installed': self.check_python_dependencies(),
            'tally_accessible': self.check_tally_prime_connection(),
            'system': self.system,
            'architecture': self.architecture
        }
    
    def check_python_dependencies(self) -> bool:
        """Check if Python dependencies are installed."""
        try:
            import PySide6
            import requests
            import supabase
            return True
        except ImportError:
            return False
    
    def install_all_dependencies(self, install_dir: Path = None) -> bool:
        """Install all required dependencies."""
        print("Installing all dependencies...")
        
        # Install Python first
        if not self.check_python_installed():
            print("Python not found. Installing...")
            if not self.install_python(install_dir):
                print("Failed to install Python")
                return False
        
        # Install Python dependencies
        if not self.check_python_dependencies():
            print("Python dependencies not found. Installing...")
            if not self.install_python_dependencies():
                print("Failed to install Python dependencies")
                return False
        
        # Check Tally connection
        if not self.check_tally_prime_connection():
            print("Warning: Tally Prime not accessible. Please ensure Tally is running on localhost:9000")
        
        print("All dependencies installed successfully")
        return True


def main():
    """Main function for testing."""
    manager = DependencyManager()
    
    print("=== Dependency Manager Test ===")
    print(f"System: {manager.system}")
    print(f"Architecture: {manager.architecture}")
    
    status = manager.get_installation_status()
    print("\nInstallation Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if not all([status['python_installed'], status['python_dependencies_installed']]):
        print("\nInstalling missing dependencies...")
        manager.install_all_dependencies()


if __name__ == "__main__":
    main() 
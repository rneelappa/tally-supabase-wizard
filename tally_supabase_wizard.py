#!/usr/bin/env python3
"""
Tally Supabase Wizard
A streamlined wizard for synchronizing Tally Prime data to Supabase.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, 
    QFormLayout, QLabel, QLineEdit, QPushButton, QTextEdit, 
    QProgressBar, QGroupBox, QMessageBox, QCheckBox, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont

from dependency_manager import DependencyManager
from supabase_config_page import SupabaseConfigPage
from tally_supabase_sync import TallySupabaseSync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DependencyCheckPage(QWizardPage):
    """Page for checking and installing dependencies."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Dependency Check")
        self.setSubTitle("Checking and installing required dependencies.")
        
        self.dependency_manager = DependencyManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Status group
        status_group = QGroupBox("Dependency Status")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        # Check button
        self.check_button = QPushButton("Check Dependencies")
        self.check_button.clicked.connect(self.check_dependencies)
        status_layout.addWidget(self.check_button)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        self.setLayout(layout)
    
    def check_dependencies(self):
        """Check and install dependencies."""
        self.check_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start dependency check thread
        self.check_thread = DependencyCheckThread(self.dependency_manager)
        self.check_thread.progress_update.connect(self.on_progress_update)
        self.check_thread.check_complete.connect(self.on_check_complete)
        self.check_thread.start()
    
    def on_progress_update(self, message: str):
        """Handle progress updates."""
        self.status_text.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_check_complete(self, success: bool, message: str):
        """Handle check completion."""
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_text.append("✅ All dependencies are ready!")
            self.completeChanged.emit()
        else:
            self.status_text.append(f"❌ {message}")
    
    def isComplete(self) -> bool:
        """Check if page is complete."""
        return hasattr(self, 'check_thread') and hasattr(self.check_thread, 'success') and self.check_thread.success


class DependencyCheckThread(QThread):
    """Thread for checking dependencies."""
    
    progress_update = Signal(str)
    check_complete = Signal(bool, str)
    
    def __init__(self, dependency_manager: DependencyManager):
        super().__init__()
        self.dependency_manager = dependency_manager
        self.success = False
    
    def run(self):
        """Run dependency check."""
        try:
            self.progress_update.emit("Checking Python installation...")
            
            # Check Python
            if not self.dependency_manager.check_python_installed():
                self.progress_update.emit("Python 3.11+ not found. Installing...")
                if not self.dependency_manager.install_python():
                    self.check_complete.emit(False, "Failed to install Python")
                    return
            
            self.progress_update.emit("✅ Python is ready")
            
            # Check Python dependencies
            self.progress_update.emit("Installing Python dependencies...")
            if not self.dependency_manager.install_python_dependencies():
                self.check_complete.emit(False, "Failed to install Python dependencies")
                return
            
            self.progress_update.emit("✅ Python dependencies installed")
            
            # Check Tally connection
            self.progress_update.emit("Checking Tally Prime connection...")
            if not self.dependency_manager.check_tally_prime_connection():
                self.progress_update.emit("⚠️  Tally Prime not accessible. Please ensure Tally is running on localhost:9000")
            
            self.success = True
            self.check_complete.emit(True, "All dependencies are ready")
            
        except Exception as e:
            self.check_complete.emit(False, f"Dependency check failed: {str(e)}")


class WelcomePage(QWizardPage):
    """Welcome page for the wizard."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to Tally Supabase Wizard")
        self.setSubTitle("Sync your Tally Prime data to Supabase database.")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_text = QLabel(
            "This wizard will help you:\n\n"
            "• Connect to your Supabase database\n"
            "• Analyze your Tally Prime data structure\n"
            "• Create database tables that match your Tally schema\n"
            "• Synchronize all your Tally data to Supabase\n"
            "• Access your data through Supabase's REST API\n\n"
            "Make sure Tally Prime is running and accessible on localhost:9000"
        )
        welcome_text.setWordWrap(True)
        welcome_text.setStyleSheet("font-size: 14px; line-height: 1.5;")
        layout.addWidget(welcome_text)
        
        # Prerequisites
        prereq_group = QGroupBox("Prerequisites")
        prereq_layout = QVBoxLayout()
        
        prereq_text = QLabel(
            "Before starting, ensure you have:\n"
            "• Tally Prime running and accessible\n"
            "• Supabase project created\n"
            "• Supabase API key ready"
        )
        prereq_text.setWordWrap(True)
        prereq_layout.addWidget(prereq_text)
        
        prereq_group.setLayout(prereq_layout)
        layout.addWidget(prereq_group)
        
        self.setLayout(layout)


class FinalPage(QWizardPage):
    """Final page showing completion status."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Synchronization Complete")
        self.setSubTitle("Your Tally data has been successfully synchronized to Supabase.")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Success message
        success_text = QLabel(
            "🎉 Congratulations! Your Tally data has been successfully synchronized to Supabase.\n\n"
            "You can now:\n"
            "• Access your data through Supabase's REST API\n"
            "• Use Supabase's real-time features\n"
            "• Build applications on top of your Tally data\n"
            "• Set up automated sync schedules\n\n"
            "Your data is now available at your Supabase project URL."
        )
        success_text.setWordWrap(True)
        success_text.setStyleSheet("font-size: 14px; line-height: 1.5;")
        layout.addWidget(success_text)
        
        # API access info
        api_group = QGroupBox("API Access Information")
        api_layout = QVBoxLayout()
        
        self.api_info = QTextEdit()
        self.api_info.setMaximumHeight(150)
        self.api_info.setReadOnly(True)
        api_layout.addWidget(self.api_info)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Initialize the page with API information."""
        supabase_url = self.wizard().property("supabase_url")
        if supabase_url:
            api_text = f"""Your Supabase API endpoints:

Companies: {supabase_url}/rest/v1/tally_companies
Ledgers: {supabase_url}/rest/v1/tally_ledgers
Vouchers: {supabase_url}/rest/v1/tally_vouchers
Divisions: {supabase_url}/rest/v1/tally_divisions

Use your API key in the 'apikey' header for authentication."""
            
            self.api_info.setText(api_text)


class TallySupabaseWizard(QWizard):
    """Main wizard for Tally to Supabase synchronization."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Tally Supabase Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(600, 500)
        
        # Set up pages
        self.addPage(DependencyCheckPage())
        self.addPage(WelcomePage())
        self.addPage(SupabaseConfigPage())
        self.addPage(FinalPage())
        
        # Connect signals
        self.finished.connect(self.on_wizard_finished)
        
        # Load configuration
        self.load_configuration()
    
    def load_configuration(self):
        """Load existing configuration."""
        config_dir = Path.home() / ".tally-tunnel"
        config_file = config_dir / "config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Set wizard properties from config
                if 'supabase_url' in config:
                    self.setProperty("supabase_url", config['supabase_url'])
                if 'supabase_key' in config:
                    self.setProperty("supabase_key", config['supabase_key'])
                    
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
    
    def on_wizard_finished(self, result: int):
        """Handle wizard completion."""
        if result == 1:  # QWizard.Accepted
            QMessageBox.information(
                self, 
                "Setup Complete", 
                "Tally Supabase synchronization has been configured successfully!\n\n"
                "You can now access your Tally data through your Supabase project."
            )
        else:
            QMessageBox.information(
                self,
                "Setup Cancelled",
                "Setup was cancelled. You can run the wizard again anytime."
            )


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Tally Supabase Wizard")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show wizard
    wizard = TallySupabaseWizard()
    wizard.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
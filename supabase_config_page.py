#!/usr/bin/env python3
"""
Supabase Configuration Page for Tally Tunnel Wizard
Handles Supabase setup and data synchronization configuration.
"""

import sys
import json
from typing import Dict, Any
from pathlib import Path

from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QGroupBox, QMessageBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont

from supabase_manager import SupabaseManager
from tally_supabase_sync import TallySupabaseSync


class SupabaseConnectionThread(QThread):
    """Thread for testing Supabase connection."""
    
    connection_result = Signal(bool, str)
    
    def __init__(self, project_url: str, api_key: str):
        super().__init__()
        self.project_url = project_url
        self.api_key = api_key
    
    def run(self):
        """Test Supabase connection."""
        try:
            manager = SupabaseManager(self.project_url, self.api_key)
            connected = manager.test_connection()
            
            if connected:
                tables = manager.get_existing_tables()
                message = f"Connected successfully! Found {len(tables)} existing tables."
            else:
                message = "Connection failed. Please check your credentials."
            
            self.connection_result.emit(connected, message)
            
        except Exception as e:
            self.connection_result.emit(False, f"Connection error: {str(e)}")


class TallyAnalysisThread(QThread):
    """Thread for analyzing Tally data structure."""
    
    analysis_complete = Signal(dict)
    analysis_progress = Signal(str)
    
    def __init__(self, supabase_url: str, supabase_key: str):
        super().__init__()
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
    
    def run(self):
        """Analyze Tally data structure."""
        try:
            self.analysis_progress.emit("Initializing Tally connection...")
            sync = TallySupabaseSync(self.supabase_url, self.supabase_key)
            
            self.analysis_progress.emit("Validating Tally connection...")
            if not sync.validate_tally_connection():
                self.analysis_complete.emit({'error': 'Tally connection failed'})
                return
            
            self.analysis_progress.emit("Analyzing Tally data structure...")
            structure = sync.analyze_tally_structure()
            
            self.analysis_progress.emit("Creating sync plan...")
            plan = sync.preview_sync_plan(structure)
            
            result = {
                'structure': structure,
                'plan': plan,
                'sync': sync
            }
            
            self.analysis_complete.emit(result)
            
        except Exception as e:
            self.analysis_complete.emit({'error': str(e)})


class DataSyncThread(QThread):
    """Thread for synchronizing data to Supabase."""
    
    sync_progress = Signal(str)
    sync_complete = Signal(bool, str)
    
    def __init__(self, sync: TallySupabaseSync, structure: dict, mapping: dict):
        super().__init__()
        self.sync = sync
        self.structure = structure
        self.mapping = mapping
    
    def run(self):
        """Sync data to Supabase."""
        try:
            self.sync_progress.emit("Starting data synchronization...")
            success = self.sync.sync_data_to_supabase(self.structure, self.mapping)
            
            if success:
                self.sync_complete.emit(True, "Data synchronization completed successfully!")
            else:
                self.sync_complete.emit(False, "Data synchronization failed. Check logs for details.")
                
        except Exception as e:
            self.sync_complete.emit(False, f"Sync error: {str(e)}")


class SupabaseConfigPage(QWizardPage):
    """Page for configuring Supabase connection and data synchronization."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Supabase Configuration")
        self.setSubTitle("Configure Supabase connection and manage Tally data synchronization.")
        
        self.supabase_manager = None
        self.sync_manager = None
        self.structure_data = None
        self.sync_plan = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Supabase Connection Group
        connection_group = QGroupBox("Supabase Connection")
        connection_layout = QFormLayout()
        
        self.project_url_edit = QLineEdit("https://ppfwlhfehwelinfprviw.supabase.co")
        self.project_url_edit.setPlaceholderText("Enter Supabase project URL")
        connection_layout.addRow("Project URL:", self.project_url_edit)
        
        self.api_key_edit = QLineEdit("sb_secret_0ng3_U_wd2MXRyzPYXweuw_dDl-5EAA")
        self.api_key_edit.setPlaceholderText("Enter Supabase API key")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        connection_layout.addRow("API Key:", self.api_key_edit)
        
        # Test connection button
        test_button_layout = QHBoxLayout()
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self.test_connection)
        test_button_layout.addWidget(self.test_connection_button)
        
        self.connection_status = QLabel("Not tested")
        self.connection_status.setStyleSheet("color: gray;")
        test_button_layout.addWidget(self.connection_status)
        
        connection_layout.addRow("", test_button_layout)
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # Tally Analysis Group
        analysis_group = QGroupBox("Tally Data Analysis")
        analysis_layout = QVBoxLayout()
        
        self.analyze_button = QPushButton("Analyze Tally Data Structure")
        self.analyze_button.clicked.connect(self.analyze_tally_data)
        self.analyze_button.setEnabled(False)
        analysis_layout.addWidget(self.analyze_button)
        
        self.analysis_progress = QLabel("Click 'Analyze Tally Data Structure' to start")
        self.analysis_progress.setStyleSheet("color: gray;")
        analysis_layout.addWidget(self.analysis_progress)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Sync Plan Group
        self.sync_plan_group = QGroupBox("Synchronization Plan")
        self.sync_plan_group.setVisible(False)
        sync_plan_layout = QVBoxLayout()
        
        self.sync_plan_text = QTextEdit()
        self.sync_plan_text.setMaximumHeight(150)
        self.sync_plan_text.setReadOnly(True)
        sync_plan_layout.addWidget(self.sync_plan_text)
        
        # Sync button
        self.sync_button = QPushButton("Start Data Synchronization")
        self.sync_button.clicked.connect(self.start_sync)
        self.sync_button.setEnabled(False)
        sync_plan_layout.addWidget(self.sync_button)
        
        self.sync_progress = QLabel("")
        self.sync_progress.setStyleSheet("color: gray;")
        sync_plan_layout.addWidget(self.sync_progress)
        
        self.sync_plan_group.setLayout(sync_plan_layout)
        layout.addWidget(self.sync_plan_group)
        
        # Log Group
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        self.setLayout(layout)
    
    def test_connection(self):
        """Test Supabase connection."""
        project_url = self.project_url_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        
        if not project_url or not api_key:
            QMessageBox.warning(self, "Missing Information", "Please enter both Project URL and API Key.")
            return
        
        self.test_connection_button.setEnabled(False)
        self.connection_status.setText("Testing...")
        self.connection_status.setStyleSheet("color: orange;")
        
        # Start connection test thread
        self.connection_thread = SupabaseConnectionThread(project_url, api_key)
        self.connection_thread.connection_result.connect(self.on_connection_result)
        self.connection_thread.start()
    
    def on_connection_result(self, connected: bool, message: str):
        """Handle connection test result."""
        self.test_connection_button.setEnabled(True)
        
        if connected:
            self.connection_status.setText("✅ Connected")
            self.connection_status.setStyleSheet("color: green;")
            self.analyze_button.setEnabled(True)
            
            # Store connection info
            self.wizard().setProperty("supabase_url", self.project_url_edit.text().strip())
            self.wizard().setProperty("supabase_key", self.api_key_edit.text().strip())
            
        else:
            self.connection_status.setText("❌ Failed")
            self.connection_status.setStyleSheet("color: red;")
            self.analyze_button.setEnabled(False)
        
        self.log_message(message)
    
    def analyze_tally_data(self):
        """Analyze Tally data structure."""
        supabase_url = self.project_url_edit.text().strip()
        supabase_key = self.api_key_edit.text().strip()
        
        self.analyze_button.setEnabled(False)
        self.analysis_progress.setText("Analyzing...")
        self.analysis_progress.setStyleSheet("color: orange;")
        
        # Start analysis thread
        self.analysis_thread = TallyAnalysisThread(supabase_url, supabase_key)
        self.analysis_thread.analysis_progress.connect(self.on_analysis_progress)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.start()
    
    def on_analysis_progress(self, message: str):
        """Handle analysis progress updates."""
        self.analysis_progress.setText(message)
        self.log_message(message)
    
    def on_analysis_complete(self, result: Dict[str, Any]):
        """Handle analysis completion."""
        self.analyze_button.setEnabled(True)
        
        if 'error' in result:
            self.analysis_progress.setText(f"❌ Analysis failed: {result['error']}")
            self.analysis_progress.setStyleSheet("color: red;")
            self.log_message(f"Analysis failed: {result['error']}")
        else:
            self.analysis_progress.setText("✅ Analysis completed")
            self.analysis_progress.setStyleSheet("color: green;")
            
            # Store results
            self.structure_data = result['structure']
            self.sync_plan = result['plan']
            self.sync_manager = result['sync']
            
            # Show sync plan
            self.show_sync_plan()
            
            self.log_message("Analysis completed successfully")
    
    def show_sync_plan(self):
        """Display the synchronization plan."""
        if not self.sync_plan:
            return
        
        plan_text = "Synchronization Plan:\n\n"
        
        # Tables to create
        if self.sync_plan['tables_to_create']:
            plan_text += f"Tables to create: {', '.join(self.sync_plan['tables_to_create'])}\n"
        
        # Tables to update
        if self.sync_plan['tables_to_update']:
            plan_text += f"Tables to update: {', '.join(self.sync_plan['tables_to_update'])}\n"
        
        plan_text += f"\nEstimated total records: {self.sync_plan['estimated_records']}\n\n"
        
        # Data summary
        plan_text += "Data Summary:\n"
        for table_name, info in self.sync_plan['data_summary'].items():
            plan_text += f"  {table_name}: {info['record_count']} records from {info['source']}\n"
        
        self.sync_plan_text.setText(plan_text)
        self.sync_plan_group.setVisible(True)
        self.sync_button.setEnabled(True)
    
    def start_sync(self):
        """Start data synchronization."""
        if not self.sync_manager or not self.structure_data:
            QMessageBox.warning(self, "No Data", "Please analyze Tally data first.")
            return
        
        # Ask for confirmation
        response = QMessageBox.question(
            self, 
            "Confirm Sync", 
            f"This will sync {self.sync_plan['estimated_records']} records to Supabase. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if response != QMessageBox.Yes:
            return
        
        self.sync_button.setEnabled(False)
        self.sync_progress.setText("Synchronizing...")
        self.sync_progress.setStyleSheet("color: orange;")
        
        # Create mapping
        mapping = self.sync_manager.create_table_mapping(self.structure_data)
        
        # Start sync thread
        self.sync_thread = DataSyncThread(self.sync_manager, self.structure_data, mapping)
        self.sync_thread.sync_progress.connect(self.on_sync_progress)
        self.sync_thread.sync_complete.connect(self.on_sync_complete)
        self.sync_thread.start()
    
    def on_sync_progress(self, message: str):
        """Handle sync progress updates."""
        self.sync_progress.setText(message)
        self.log_message(message)
    
    def on_sync_complete(self, success: bool, message: str):
        """Handle sync completion."""
        self.sync_button.setEnabled(True)
        
        if success:
            self.sync_progress.setText("✅ Sync completed")
            self.sync_progress.setStyleSheet("color: green;")
        else:
            self.sync_progress.setText("❌ Sync failed")
            self.sync_progress.setStyleSheet("color: red;")
        
        self.log_message(message)
        
        if success:
            QMessageBox.information(self, "Success", "Data synchronization completed successfully!")
    
    def log_message(self, message: str):
        """Add message to log."""
        timestamp = QTimer().remainingTime()  # Simple timestamp
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        # Check if connection is established
        if not self.wizard().property("supabase_url"):
            QMessageBox.warning(self, "Missing Configuration", "Please test and establish Supabase connection.")
            return False
        
        # Check if analysis is completed
        if not self.structure_data:
            QMessageBox.warning(self, "Missing Analysis", "Please analyze Tally data structure.")
            return False
        
        return True


def main():
    """Test the Supabase configuration page."""
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    page = SupabaseConfigPage()
    page.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Supabase Configuration Page
Handles Supabase connection and Tally data synchronization.
"""

import logging
from typing import Dict, Any

from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QProgressBar, QGroupBox, 
    QMessageBox, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import QThread, Signal

from supabase_manager import SupabaseManager
from tally_http_client import TallyHTTPClient
from tally_supabase_sync import TallySupabaseSync

logger = logging.getLogger(__name__)


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
            if manager.test_connection():
                self.connection_result.emit(True, "Connected successfully!")
            else:
                self.connection_result.emit(False, "Connection failed")
        except Exception as e:
            self.connection_result.emit(False, f"Connection error: {str(e)}")


class TallyAnalysisThread(QThread):
    """Thread for analyzing Tally data structure."""
    
    analysis_complete = Signal(dict)
    analysis_progress = Signal(str)
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        """Analyze Tally data structure."""
        try:
            self.analysis_progress.emit("Initializing Tally connection...")
            
            # Create Tally client
            tally_client = TallyHTTPClient()
            
            # Create sync instance with Tally client
            sync = TallySupabaseSync(tally_client)
            
            self.analysis_progress.emit("Testing Tally connection...")
            if not tally_client.test_connection():
                self.analysis_complete.emit({'error': 'Tally connection failed'})
                return
            
            self.analysis_progress.emit("Analyzing Tally data structure...")
            metadata = sync.analyze_tally_data()
            
            if "error" in metadata:
                self.analysis_complete.emit({'error': metadata["error"]})
                return
            
            self.analysis_progress.emit("Generating sync recommendations...")
            recommendations = sync.get_sync_recommendations(metadata)
            
            self.analysis_progress.emit("Validating data quality...")
            quality = sync.validate_data_quality(metadata)
            
            self.analysis_progress.emit("Preparing sync data...")
            sync_data = sync.prepare_sync_data(metadata)
            
            result = {
                'metadata': metadata,
                'recommendations': recommendations,
                'quality': quality,
                'sync_data': sync_data,
                'tally_client': tally_client,
                'sync': sync
            }
            
            self.analysis_complete.emit(result)
            
        except Exception as e:
            self.analysis_complete.emit({'error': str(e)})


class DataSyncThread(QThread):
    """Thread for synchronizing data to Supabase."""
    
    sync_progress = Signal(str)
    sync_complete = Signal(bool, str)
    
    def __init__(self, supabase_manager: SupabaseManager, sync_data: dict):
        super().__init__()
        self.supabase_manager = supabase_manager
        self.sync_data = sync_data
    
    def run(self):
        """Sync data to Supabase."""
        try:
            self.sync_progress.emit("Starting data synchronization...")
            
            # Sync each data type
            total_synced = 0
            
            for data_type, data_list in self.sync_data.items():
                if data_list and len(data_list) > 0:
                    self.sync_progress.emit(f"Syncing {data_type} ({len(data_list)} records)...")
                    
                    # Create table name
                    table_name = f"tally_{data_type}"
                    
                    # Sync to Supabase
                    if self.supabase_manager.sync_tally_data({table_name: data_list}):
                        total_synced += len(data_list)
                        self.sync_progress.emit(f"✅ Synced {len(data_list)} {data_type}")
                    else:
                        self.sync_progress.emit(f"❌ Failed to sync {data_type}")
            
            if total_synced > 0:
                self.sync_complete.emit(True, f"Data synchronization completed! Synced {total_synced} total records.")
            else:
                self.sync_complete.emit(False, "No data was synced. Check logs for details.")
                
        except Exception as e:
            self.sync_complete.emit(False, f"Sync error: {str(e)}")


class SupabaseConfigPage(QWizardPage):
    """Page for configuring Supabase connection and data synchronization."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Supabase Configuration")
        self.setSubTitle("Configure Supabase connection and manage Tally data synchronization.")
        
        self.supabase_manager = None
        self.tally_client = None
        self.sync_manager = None
        self.metadata = None
        self.recommendations = None
        self.sync_data = None
        
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
        
        # Analysis button
        self.analyze_button = QPushButton("Analyze Tally Data")
        self.analyze_button.clicked.connect(self.analyze_tally_data)
        analysis_layout.addWidget(self.analyze_button)
        
        # Analysis progress
        self.analysis_progress = QTextEdit()
        self.analysis_progress.setMaximumHeight(150)
        self.analysis_progress.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_progress)
        
        # Analysis results
        self.analysis_results = QTextEdit()
        self.analysis_results.setMaximumHeight(200)
        self.analysis_results.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_results)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Sync Group
        sync_group = QGroupBox("Data Synchronization")
        sync_layout = QVBoxLayout()
        
        # Sync button
        self.sync_button = QPushButton("Start Sync")
        self.sync_button.clicked.connect(self.start_sync)
        self.sync_button.setEnabled(False)
        sync_layout.addWidget(self.sync_button)
        
        # Sync progress
        self.sync_progress = QTextEdit()
        self.sync_progress.setMaximumHeight(150)
        self.sync_progress.setReadOnly(True)
        sync_layout.addWidget(self.sync_progress)
        
        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)
        
        self.setLayout(layout)
    
    def test_connection(self):
        """Test Supabase connection."""
        self.test_connection_button.setEnabled(False)
        self.connection_status.setText("Testing...")
        self.connection_status.setStyleSheet("color: orange;")
        
        # Start connection test thread
        self.connection_thread = SupabaseConnectionThread(
            self.project_url_edit.text(),
            self.api_key_edit.text()
        )
        self.connection_thread.connection_result.connect(self.on_connection_result)
        self.connection_thread.start()
    
    def on_connection_result(self, connected: bool, message: str):
        """Handle connection test result."""
        self.test_connection_button.setEnabled(True)
        
        if connected:
            self.connection_status.setText("✅ Connected")
            self.connection_status.setStyleSheet("color: green;")
            
            # Create Supabase manager
            self.supabase_manager = SupabaseManager(
                self.project_url_edit.text(),
                self.api_key_edit.text()
            )
            
            # Enable analysis button
            self.analyze_button.setEnabled(True)
            
        else:
            self.connection_status.setText("❌ Failed")
            self.connection_status.setStyleSheet("color: red;")
        
        self.log_message(message)
    
    def analyze_tally_data(self):
        """Analyze Tally data structure."""
        self.analyze_button.setEnabled(False)
        self.analysis_progress.clear()
        self.analysis_results.clear()
        
        # Start analysis thread
        self.analysis_thread = TallyAnalysisThread()
        self.analysis_thread.analysis_progress.connect(self.on_analysis_progress)
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.start()
    
    def on_analysis_progress(self, message: str):
        """Handle analysis progress updates."""
        self.analysis_progress.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.analysis_progress.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_analysis_complete(self, result: Dict[str, Any]):
        """Handle analysis completion."""
        self.analyze_button.setEnabled(True)
        
        if "error" in result:
            self.analysis_results.append(f"❌ Analysis failed: {result['error']}")
            return
        
        # Store results
        self.metadata = result['metadata']
        self.recommendations = result['recommendations']
        self.sync_data = result['sync_data']
        self.tally_client = result['tally_client']
        self.sync_manager = result['sync']
        
        # Display results
        summary = self.metadata.get('summary', {})
        self.analysis_results.append("📊 Analysis Results:")
        self.analysis_results.append(f"  • Companies: {summary.get('total_companies', 0)}")
        self.analysis_results.append(f"  • Groups: {summary.get('total_groups', 0)}")
        self.analysis_results.append(f"  • Ledgers: {summary.get('total_ledgers', 0)}")
        self.analysis_results.append(f"  • Divisions: {summary.get('total_divisions', 0)}")
        self.analysis_results.append(f"  • Vouchers: {summary.get('total_vouchers', 0)}")
        
        # Show quality score
        quality = result['quality']
        if quality.get('valid', False):
            self.analysis_results.append(f"  • Data Quality: ✅ Good ({quality.get('data_quality_score', 0)}%)")
        else:
            self.analysis_results.append(f"  • Data Quality: ⚠️ Issues found")
            for issue in quality.get('issues', []):
                self.analysis_results.append(f"    - {issue}")
        
        # Enable sync button
        self.sync_button.setEnabled(True)
    
    def start_sync(self):
        """Start data synchronization."""
        if not self.supabase_manager or not self.sync_data:
            QMessageBox.warning(self, "Error", "Please analyze Tally data first.")
            return
        
        self.sync_button.setEnabled(False)
        self.sync_progress.clear()
        
        # Start sync thread
        self.sync_thread = DataSyncThread(self.supabase_manager, self.sync_data)
        self.sync_thread.sync_progress.connect(self.on_sync_progress)
        self.sync_thread.sync_complete.connect(self.on_sync_complete)
        self.sync_thread.start()
    
    def on_sync_progress(self, message: str):
        """Handle sync progress updates."""
        self.sync_progress.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.sync_progress.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_sync_complete(self, success: bool, message: str):
        """Handle sync completion."""
        self.sync_button.setEnabled(True)
        
        if success:
            self.sync_progress.append(f"✅ {message}")
            QMessageBox.information(self, "Success", message)
        else:
            self.sync_progress.append(f"❌ {message}")
            QMessageBox.warning(self, "Sync Failed", message)
    
    def log_message(self, message: str):
        """Log a message to the analysis progress."""
        self.analysis_progress.append(message)
        
        # Auto-scroll to bottom
        scrollbar = self.analysis_progress.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def validatePage(self) -> bool:
        """Validate the page before proceeding."""
        if not self.supabase_manager:
            QMessageBox.warning(self, "Validation Error", "Please test Supabase connection first.")
            return False
        
        if not self.metadata:
            QMessageBox.warning(self, "Validation Error", "Please analyze Tally data first.")
            return False
        
        return True


def main():
    """Test the Supabase configuration page."""
    from PySide6.QtWidgets import QApplication
    
    app = QApplication([])
    
    page = SupabaseConfigPage()
    page.show()
    
    app.exec()


if __name__ == "__main__":
    main() 
"""
Unit tests for EULA manager.
"""

import pytest
import os
from pathlib import Path
from password_analyzer.eula import EULAManager


class TestEULAManager:
    """Test suite for EULAManager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Use a temporary test directory
        self.test_dir = Path("test_config")
        self.test_dir.mkdir(exist_ok=True)
        self.eula = EULAManager(config_dir=str(self.test_dir))
    
    def teardown_method(self):
        """Cleanup test files."""
        # Remove test files
        if self.eula.eula_file.exists():
            self.eula.eula_file.unlink()
        if self.eula.log_file.exists():
            self.eula.log_file.unlink()
        if self.test_dir.exists():
            self.test_dir.rmdir()
    
    def test_eula_not_accepted_initially(self):
        """Test that EULA is not accepted by default."""
        assert not self.eula.check_eula_accepted()
    
    def test_accept_eula(self):
        """Test EULA acceptance."""
        result = self.eula.accept_eula()
        
        assert result == True
        assert self.eula.check_eula_accepted()
        assert self.eula.eula_file.exists()
    
    def test_eula_file_content(self):
        """Test that EULA file contains expected content."""
        self.eula.accept_eula()
        
        with open(self.eula.eula_file, 'r') as f:
            content = f.read()
        
        assert "EULA Accepted" in content
        assert "Version" in content
    
    def test_get_eula_text(self):
        """Test EULA text retrieval."""
        text = self.eula.get_eula_text()
        
        assert "END USER LICENSE AGREEMENT" in text
        assert "PERMITTED USES" in text
        assert "PROHIBITED USES" in text
        assert "LEGAL DISCLAIMER" in text
    
    def test_log_action(self):
        """Test action logging."""
        self.eula.log_action("test_action", "test_details")
        
        assert self.eula.log_file.exists()
        
        with open(self.eula.log_file, 'r') as f:
            content = f.read()
        
        assert "test_action" in content
        assert "test_details" in content
    
    def test_multiple_log_entries(self):
        """Test multiple log entries."""
        self.eula.log_action("action1")
        self.eula.log_action("action2", "details2")
        
        with open(self.eula.log_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) >= 2
        assert any("action1" in line for line in lines)
        assert any("action2" in line for line in lines)
    
    def test_get_export_warning(self):
        """Test export warning text."""
        warning = self.eula.get_export_warning()
        
        assert "WORDLIST EXPORT" in warning
        assert "CONFIRMATION REQUIRED" in warning
        assert "ILLEGAL" in warning
    
    def test_confirm_export_cli(self):
        """Test CLI export confirmation (should return False)."""
        # CLI confirmation requires explicit flag, not interactive
        result = self.eula.confirm_export_cli()
        assert result == False
    
    def test_confirm_export_gui(self):
        """Test GUI export confirmation."""
        # GUI confirmation should return True (actual confirmation is in GUI)
        result = self.eula.confirm_export_gui()
        assert result == True
    
    def test_config_directory_creation(self):
        """Test that config directory is created."""
        new_dir = Path("test_new_config")
        if new_dir.exists():
            new_dir.rmdir()
        
        eula = EULAManager(config_dir=str(new_dir))
        
        assert new_dir.exists()
        
        # Cleanup
        new_dir.rmdir()
    
    def test_log_action_with_empty_details(self):
        """Test logging action without details."""
        self.eula.log_action("simple_action")
        
        with open(self.eula.log_file, 'r') as f:
            content = f.read()
        
        assert "simple_action" in content
    
    def test_timestamp_in_log(self):
        """Test that log entries include timestamps."""
        self.eula.log_action("test")
        
        with open(self.eula.log_file, 'r') as f:
            content = f.read()
        
        # Should contain ISO format date/time
        assert "-" in content  # Date separator
        assert ":" in content  # Time separator

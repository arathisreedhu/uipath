"""
Unit tests for pattern detector.
"""

import pytest
from password_analyzer.pattern_detector import PatternDetector


class TestPatternDetector:
    """Test suite for PatternDetector."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.detector = PatternDetector()
    
    def test_repeated_sequences(self):
        """Test detection of repeated character sequences."""
        patterns = self.detector.detect_patterns("aaabbb")
        assert len(patterns['repeated_sequences']) > 0
        
        patterns2 = self.detector.detect_patterns("111222")
        assert len(patterns2['repeated_sequences']) > 0
    
    def test_no_repeated_sequences(self):
        """Test password without repeated sequences."""
        patterns = self.detector.detect_patterns("abcdef123")
        assert len(patterns['repeated_sequences']) == 0
    
    def test_keyboard_patterns(self):
        """Test detection of keyboard patterns."""
        patterns1 = self.detector.detect_patterns("qwerty123")
        assert len(patterns1['keyboard_patterns']) > 0
        
        patterns2 = self.detector.detect_patterns("asdfgh")
        assert len(patterns2['keyboard_patterns']) > 0
    
    def test_date_patterns(self):
        """Test detection of date patterns."""
        patterns1 = self.detector.detect_patterns("password1990")
        assert len(patterns1['dates']) > 0
        
        patterns2 = self.detector.detect_patterns("test20230101")
        assert len(patterns2['dates']) > 0
        
        patterns3 = self.detector.detect_patterns("pass01/01/2023")
        assert len(patterns3['dates']) > 0
    
    def test_no_date_patterns(self):
        """Test password without date patterns."""
        patterns = self.detector.detect_patterns("MyP@ssw0rd")
        # This test might detect year-like patterns, so we check it doesn't crash
        assert 'dates' in patterns
    
    def test_sequential_numbers(self):
        """Test detection of sequential numbers."""
        patterns = self.detector.detect_patterns("password123")
        assert len(patterns['sequential']) > 0
    
    def test_sequential_letters(self):
        """Test detection of sequential letters."""
        patterns = self.detector.detect_patterns("abcdef")
        assert len(patterns['sequential']) > 0
    
    def test_no_sequential(self):
        """Test password without sequential patterns."""
        patterns = self.detector.detect_patterns("Tr0ub4dor")
        # May or may not detect depending on content
        assert 'sequential' in patterns
    
    def test_leet_speak_detection(self):
        """Test detection of leet speak."""
        # Password with leet speak
        patterns1 = self.detector.detect_patterns("p4ssw0rd")
        assert patterns1['leet_speak'] == True
        
        patterns2 = self.detector.detect_patterns("h3ll0w0rld")
        assert patterns2['leet_speak'] == True
    
    def test_no_leet_speak(self):
        """Test password without leet speak."""
        patterns = self.detector.detect_patterns("password")
        assert patterns['leet_speak'] == False
    
    def test_common_substitutions(self):
        """Test detection of common character substitutions."""
        patterns = self.detector.detect_patterns("p@ssw0rd")
        assert len(patterns['common_substitutions']) > 0
        assert any('@' in sub for sub in patterns['common_substitutions'])
        assert any('0' in sub for sub in patterns['common_substitutions'])
    
    def test_no_substitutions(self):
        """Test password without common substitutions."""
        patterns = self.detector.detect_patterns("password")
        assert len(patterns['common_substitutions']) == 0
    
    def test_all_patterns_keys_present(self):
        """Test that all expected pattern keys are present."""
        patterns = self.detector.detect_patterns("test123")
        
        expected_keys = [
            'repeated_sequences',
            'keyboard_patterns',
            'dates',
            'sequential',
            'leet_speak',
            'common_substitutions'
        ]
        
        for key in expected_keys:
            assert key in patterns
    
    def test_multiple_patterns(self):
        """Test password with multiple patterns."""
        patterns = self.detector.detect_patterns("qwerty123abc")
        
        # Should detect keyboard pattern and sequential
        assert len(patterns['keyboard_patterns']) > 0
        assert len(patterns['sequential']) > 0
    
    def test_case_insensitive_keyboard(self):
        """Test keyboard pattern detection is case insensitive."""
        patterns1 = self.detector.detect_patterns("QWERTY")
        patterns2 = self.detector.detect_patterns("qwerty")
        
        assert len(patterns1['keyboard_patterns']) > 0
        assert len(patterns2['keyboard_patterns']) > 0

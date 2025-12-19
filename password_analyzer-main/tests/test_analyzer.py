"""
Unit tests for password analyzer module.
"""

import pytest
from password_analyzer.analyzer import PasswordAnalyzer


class TestPasswordAnalyzer:
    """Test suite for PasswordAnalyzer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = PasswordAnalyzer()
    
    def test_empty_password(self):
        """Test handling of empty password."""
        result = self.analyzer.analyze("")
        assert 'error' in result
        assert result['score'] == 0
    
    def test_weak_password(self):
        """Test analysis of weak password."""
        result = self.analyzer.analyze("password")
        assert result['zxcvbn_score'] <= 1
        assert result['overall_risk'] in ['CRITICAL', 'VERY_HIGH', 'HIGH']
    
    def test_strong_password(self):
        """Test analysis of strong password."""
        result = self.analyzer.analyze("Tr0ub4dor&3-Correct-Horse-Battery")
        assert result['zxcvbn_score'] >= 3
        assert result['overall_risk'] in ['LOW', 'VERY_LOW']
    
    def test_contextual_match(self):
        """Test detection of contextual information."""
        result = self.analyzer.analyze(
            "john1990",
            user_inputs=["john", "1990"]
        )
        assert result['has_contextual_risk']
        assert len(result['contextual_matches']) > 0
        assert result['overall_risk'] == 'CRITICAL'
    
    def test_no_contextual_match(self):
        """Test password without contextual information."""
        result = self.analyzer.analyze(
            "RandomP@ssw0rd!",
            user_inputs=["john", "smith"]
        )
        assert not result['has_contextual_risk']
        assert len(result['contextual_matches']) == 0
    
    def test_recommendations_present(self):
        """Test that recommendations are provided."""
        result = self.analyzer.analyze("weak")
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
    
    def test_pattern_detection(self):
        """Test that patterns are detected."""
        result = self.analyzer.analyze("password123")
        assert 'patterns_detected' in result
    
    def test_entropy_calculation(self):
        """Test entropy calculation."""
        result = self.analyzer.analyze("TestP@ss123", use_entropy=True)
        assert 'entropy' in result
        assert result['entropy'] is not None
        assert 'entropy_bits' in result['entropy']
    
    def test_entropy_disabled(self):
        """Test analysis without entropy calculation."""
        result = self.analyzer.analyze("TestP@ss123", use_entropy=False)
        assert result['entropy'] is None
    
    def test_batch_analyze(self):
        """Test batch password analysis."""
        passwords = ["weak", "Str0ng!P@ssw0rd", "12345"]
        results = self.analyzer.batch_analyze(passwords)
        
        assert len(results) == 3
        assert all('zxcvbn_score' in r for r in results)
    
    def test_batch_with_context(self):
        """Test batch analysis with user context."""
        passwords = ["john123", "mary456"]
        user_inputs = ["john", "mary"]
        results = self.analyzer.batch_analyze(passwords, user_inputs=user_inputs)
        
        assert len(results) == 2
        assert results[0]['has_contextual_risk']
        assert results[1]['has_contextual_risk']
    
    def test_password_length(self):
        """Test password length is recorded correctly."""
        password = "TestPassword123"
        result = self.analyzer.analyze(password)
        assert result['password_length'] == len(password)
    
    def test_risk_levels(self):
        """Test risk level calculation."""
        # Very weak password
        result1 = self.analyzer.analyze("123")
        assert result1['overall_risk'] in ['CRITICAL', 'VERY_HIGH']
        
        # Password with context
        result2 = self.analyzer.analyze("john1990", user_inputs=["john"])
        assert result2['overall_risk'] == 'CRITICAL'

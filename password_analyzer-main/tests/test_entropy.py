"""
Unit tests for entropy calculator.
"""

import pytest
from password_analyzer.entropy import EntropyCalculator


class TestEntropyCalculator:
    """Test suite for EntropyCalculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = EntropyCalculator()
    
    def test_empty_password(self):
        """Test entropy of empty password."""
        result = self.calculator.calculate("")
        assert result['entropy_bits'] == 0
        assert result['pool_size'] == 0
    
    def test_lowercase_only(self):
        """Test entropy calculation for lowercase-only password."""
        result = self.calculator.calculate("password")
        assert result['pool_size'] == 26
        assert result['entropy_bits'] > 0
    
    def test_mixed_case(self):
        """Test entropy calculation for mixed case password."""
        result = self.calculator.calculate("Password")
        assert result['pool_size'] == 52  # 26 + 26
    
    def test_with_digits(self):
        """Test entropy calculation with digits."""
        result = self.calculator.calculate("Pass123")
        assert result['pool_size'] == 62  # 26 + 26 + 10
    
    def test_with_special_characters(self):
        """Test entropy calculation with special characters."""
        result = self.calculator.calculate("Pass@123")
        assert result['pool_size'] > 62  # Includes punctuation
    
    def test_with_spaces(self):
        """Test entropy calculation with spaces."""
        result = self.calculator.calculate("Pass word 123")
        assert result['pool_size'] > 62
    
    def test_crack_times_present(self):
        """Test that crack time estimates are provided."""
        result = self.calculator.calculate("password123")
        assert 'crack_times' in result
        assert 'online_throttled' in result['crack_times']
        assert 'online_unthrottled' in result['crack_times']
        assert 'offline_slow' in result['crack_times']
        assert 'offline_fast' in result['crack_times']
    
    def test_strength_rating(self):
        """Test strength rating calculation."""
        # Very weak
        result1 = self.calculator.calculate("abc")
        assert result1['strength_rating'] == "Very Weak"
        
        # Strong
        result2 = self.calculator.calculate("ThisIsAVeryLongPassword123!@#")
        assert result2['strength_rating'] in ["Strong", "Very Strong"]
    
    def test_entropy_increases_with_length(self):
        """Test that entropy increases with password length."""
        result1 = self.calculator.calculate("pass")
        result2 = self.calculator.calculate("password")
        result3 = self.calculator.calculate("passwordpassword")
        
        assert result1['entropy_bits'] < result2['entropy_bits']
        assert result2['entropy_bits'] < result3['entropy_bits']
    
    def test_entropy_increases_with_complexity(self):
        """Test that entropy increases with character variety."""
        result1 = self.calculator.calculate("aaaaaaaa")
        result2 = self.calculator.calculate("Password")
        result3 = self.calculator.calculate("P@ssw0rd")
        
        assert result1['entropy_bits'] < result2['entropy_bits'] < result3['entropy_bits']
    
    def test_combinations_calculation(self):
        """Test total combinations calculation."""
        result = self.calculator.calculate("abc")
        expected_combinations = 26 ** 3
        assert result['total_combinations'] == expected_combinations
    
    def test_time_formatting(self):
        """Test time formatting function."""
        assert "instant" in self.calculator._format_time(0.5)
        assert "seconds" in self.calculator._format_time(30)
        assert "minutes" in self.calculator._format_time(300)
        assert "hours" in self.calculator._format_time(7200)
        assert "days" in self.calculator._format_time(86400 * 5)
        assert "years" in self.calculator._format_time(31536000 * 5)

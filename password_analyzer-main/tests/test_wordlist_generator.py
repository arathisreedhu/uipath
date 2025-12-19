"""
Unit tests for wordlist generator.
"""

import pytest
import os
from pathlib import Path
from password_analyzer.wordlist_generator import WordlistGenerator


class TestWordlistGenerator:
    """Test suite for WordlistGenerator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = WordlistGenerator()
        self.test_output = "test_wordlist.txt"
    
    def teardown_method(self):
        """Cleanup test files."""
        if os.path.exists(self.test_output):
            os.remove(self.test_output)
    
    def test_generate_wordlist_success(self):
        """Test successful wordlist generation."""
        user_inputs = ["john", "smith", "test"]
        result = self.generator.generate_educational_wordlist(
            user_inputs,
            output_path=self.test_output
        )
        
        assert result['success']
        assert os.path.exists(self.test_output)
        assert result['total_entries'] > 0
    
    def test_wordlist_file_content(self):
        """Test that generated file contains expected sections."""
        user_inputs = ["test"]
        self.generator.generate_educational_wordlist(
            user_inputs,
            output_path=self.test_output
        )
        
        with open(self.test_output, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for warning header
        assert "EDUCATIONAL WORDLIST" in content
        assert "AUTHORIZED USE ONLY" in content
        
        # Check for sections
        assert "SECTION 1" in content
        assert "SECTION 2" in content
        assert "SECTION 3" in content
        
        # Check for recommendations
        assert "PASSPHRASE" in content or "RECOMMENDED" in content
    
    def test_wordlist_size_limit(self):
        """Test that wordlist respects size limit."""
        # Generate with many inputs
        user_inputs = [f"item{i}" for i in range(100)]
        result = self.generator.generate_educational_wordlist(
            user_inputs,
            output_path=self.test_output
        )
        
        # Should be limited to MAX_ENTRIES
        assert result['total_entries'] <= self.generator.MAX_ENTRIES
    
    def test_empty_inputs(self):
        """Test handling of empty user inputs."""
        result = self.generator.generate_educational_wordlist(
            [],
            output_path=self.test_output
        )
        
        # Should still succeed with suggestions
        assert result['success']
        assert os.path.exists(self.test_output)
    
    def test_contextual_section(self):
        """Test contextual section generation."""
        user_inputs = ["john", "smith"]
        items = self.generator._generate_contextual_section(user_inputs)
        
        assert len(items) > 0
        assert "john" in items or "JOHN" in items
    
    def test_transformation_examples(self):
        """Test transformation examples generation."""
        user_inputs = ["test"]
        examples = self.generator._generate_transformation_examples(user_inputs)
        
        # Should generate some examples
        assert len(examples) > 0
    
    def test_limited_transformations(self):
        """Test that transformations are limited (not attack-ready)."""
        user_inputs = ["test"]
        examples = self.generator._generate_transformation_examples(user_inputs)
        
        # Should be educational, not exhaustive
        assert len(examples) < 100
    
    def test_leet_speak_application(self):
        """Test leet speak transformation."""
        text = "test"
        leet = self.generator._apply_leet_speak(text, max_substitutions=2)
        
        # Should be different from original
        assert leet != text
    
    def test_suggestions_generation(self):
        """Test suggestions section."""
        suggestions = self.generator._generate_suggestions()
        
        assert len(suggestions) > 0
        # Check for key recommendations
        content = ' '.join(suggestions).upper()
        assert "PASSPHRASE" in content or "PASSWORD MANAGER" in content
    
    def test_header_generation(self):
        """Test header warning generation."""
        header = self.generator._generate_header()
        
        assert "EDUCATIONAL" in header
        assert "AUTHORIZED" in header
        assert "LEGAL NOTICE" in header
    
    def test_case_variations(self):
        """Test that case variations are included."""
        user_inputs = ["Test"]
        items = self.generator._generate_contextual_section(user_inputs)
        
        # Should include different case variations
        assert "test" in items or "TEST" in items or "Test" in items
    
    def test_short_inputs_filtered(self):
        """Test that very short inputs are filtered."""
        user_inputs = ["a", "ab", "abc"]
        items = self.generator._generate_contextual_section(user_inputs)
        
        # Items shorter than 3 chars should be filtered
        assert "a" not in items
        assert "ab" not in items
    
    def test_file_encoding_utf8(self):
        """Test that file is written in UTF-8."""
        user_inputs = ["test"]
        self.generator.generate_educational_wordlist(
            user_inputs,
            output_path=self.test_output
        )
        
        # Should be able to read as UTF-8
        with open(self.test_output, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert len(content) > 0

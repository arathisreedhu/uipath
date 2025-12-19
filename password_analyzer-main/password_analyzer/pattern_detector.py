"""
Pattern detection for common password weaknesses.
"""

import re
from typing import Dict, List


class PatternDetector:
    """
    Detects common patterns in passwords that reduce security.
    """
    
    # Common keyboard patterns
    KEYBOARD_PATTERNS = [
        'qwerty', 'asdf', 'zxcv', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
        '1234567890', 'qazwsx', 'zaq1', '!qaz', '@wsx', '#edc'
    ]
    
    # Leet speak mappings
    LEET_MAPPINGS = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7', '+'],
        'l': ['1'],
        'g': ['9'],
        'b': ['8']
    }
    
    def detect_patterns(self, password: str) -> Dict[str, List[str]]:
        """
        Detect various patterns in the password.
        
        Args:
            password: The password to analyze
            
        Returns:
            Dictionary of detected patterns
        """
        return {
            'repeated_sequences': self._find_repeated_sequences(password),
            'keyboard_patterns': self._find_keyboard_patterns(password),
            'dates': self._find_dates(password),
            'sequential': self._find_sequential(password),
            'leet_speak': self._detect_leet_speak(password),
            'common_substitutions': self._find_common_substitutions(password)
        }
    
    def _find_repeated_sequences(self, password: str) -> List[str]:
        """Find repeated character sequences (e.g., 'aaa', '111')."""
        sequences = []
        pattern = r'(.)\1{2,}'  # 3 or more repeated characters
        
        for match in re.finditer(pattern, password):
            sequences.append(match.group())
        
        return sequences
    
    def _find_keyboard_patterns(self, password: str) -> List[str]:
        """Detect common keyboard patterns."""
        found = []
        password_lower = password.lower()
        
        for pattern in self.KEYBOARD_PATTERNS:
            if pattern in password_lower:
                found.append(pattern)
            # Check reverse too
            if pattern[::-1] in password_lower:
                found.append(pattern[::-1])
        
        return found
    
    def _find_dates(self, password: str) -> List[str]:
        """Detect date patterns."""
        dates = []
        
        # Common date formats
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',    # YYYY/MM/DD
            r'\d{8}',                           # YYYYMMDD or DDMMYYYY
            r'\d{6}',                           # YYMMDD or DDMMYY
            r'(19|20)\d{2}',                    # Years 1900-2099
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, password)
            dates.extend(matches)
        
        return dates
    
    def _find_sequential(self, password: str) -> List[str]:
        """Find sequential patterns (e.g., '123', 'abc')."""
        sequences = []
        
        # Check for numeric sequences
        for i in range(len(password) - 2):
            substr = password[i:i+3]
            if substr.isdigit():
                a, b, c = int(substr[0]), int(substr[1]), int(substr[2])
                if b == a + 1 and c == b + 1:
                    sequences.append(substr)
                elif b == a - 1 and c == b - 1:
                    sequences.append(substr)
        
        # Check for alphabetic sequences
        for i in range(len(password) - 2):
            substr = password[i:i+3].lower()
            if substr.isalpha():
                a, b, c = ord(substr[0]), ord(substr[1]), ord(substr[2])
                if b == a + 1 and c == b + 1:
                    sequences.append(substr)
                elif b == a - 1 and c == b - 1:
                    sequences.append(substr)
        
        return sequences
    
    def _detect_leet_speak(self, password: str) -> bool:
        """Detect if password uses leet speak substitutions."""
        leet_count = 0
        
        for char, substitutions in self.LEET_MAPPINGS.items():
            for sub in substitutions:
                if sub in password:
                    leet_count += 1
        
        # If multiple leet substitutions found, likely using leet speak
        return leet_count >= 2
    
    def _find_common_substitutions(self, password: str) -> List[str]:
        """Find common character substitutions."""
        substitutions = []
        
        common_subs = {
            '@': 'a',
            '3': 'e',
            '1': 'i',
            '!': 'i',
            '0': 'o',
            '5': 's',
            '$': 's',
            '7': 't',
            '+': 't'
        }
        
        for sub_char, original in common_subs.items():
            if sub_char in password:
                substitutions.append(f"{sub_char}→{original}")
        
        return substitutions

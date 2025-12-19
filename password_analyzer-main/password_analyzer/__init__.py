"""
Password Strength Analyzer + User-Safe Wordlist Generator

A defensive security tool for personal password analysis and education.
FOR AUTHORIZED USE ONLY.
"""

__version__ = "1.0.0"
__author__ = "Password Analyzer Team"

from .analyzer import PasswordAnalyzer
from .entropy import EntropyCalculator
from .pattern_detector import PatternDetector
from .wordlist_generator import WordlistGenerator

__all__ = [
    'PasswordAnalyzer',
    'EntropyCalculator',
    'PatternDetector',
    'WordlistGenerator'
]
